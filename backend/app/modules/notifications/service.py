# =============================================================================
# VELO Backend -- Notification Service (Phase 7.2)
# =============================================================================
#
# PUBLIC API:
#   create_notification() -- create a pending notification record.
#     Called by other modules (bookings, waitlist, payments, reminders)
#     to enqueue a notification. The processor picks it up later.
#
# INTERNAL API (used by processor):
#   resolve_notification() -- expand target into NotificationDelivery rows.
#     target_type + target_value -> individual user deliveries.
#
# TARGET RESOLUTION:
#   user:<uuid>      -> 1 delivery (direct user notification)
#   practice:<uuid>  -> N deliveries (all confirmed/attended bookings)
#   role:<role>       -> N deliveries (all users with that role)
#   all              -> N deliveries (all active users)
#
# SESSION RULES:
#   create_notification() receives a session from the caller (P-01).
#   resolve_notification() receives a session from the processor.
#   Neither calls session.commit().
# =============================================================================

from datetime import UTC, datetime
from uuid import UUID

import structlog
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.bookings.models import Booking, BookingStatus
from app.modules.notifications.models import (
    DeliveryChannel,
    DeliveryStatus,
    Notification,
    NotificationDelivery,
    NotificationStatus,
    TargetType,
)
from app.modules.users.models import User

logger = structlog.get_logger()


# ===================================================================
# Public API
# ===================================================================


async def create_notification(
    *,
    type: str,
    title: str,
    body: str,
    target_type: str,
    target_value: str,
    session: AsyncSession,
    action_data: dict | None = None,
    priority: int = 5,
    scheduled_at: datetime | None = None,
    expiry_at: datetime | None = None,
    channel: str = DeliveryChannel.TELEGRAM.value,
) -> Notification:
    """Create a pending notification for the processor to pick up.

    This is the main entry point for other modules to enqueue
    notifications. The background processor (Phase 7.2) handles
    target resolution and delivery.

    Args:
        type: Semantic notification type (e.g. reminder_24h).
        title: Human-readable title.
        body: Notification body text.
        target_type: Audience type (user, practice, role, all).
        target_value: Audience value (uuid, role name, *).
        session: Database session (caller manages commit).
        action_data: Deep link intent JSONB.
        priority: Queue priority (1=highest, default=5).
        scheduled_at: When to send (None=now).
        expiry_at: Don't send after this time.
        channel: Default delivery channel for resolved deliveries.

    Returns:
        Created Notification object.
    """
    if scheduled_at is None:
        scheduled_at = datetime.now(UTC)

    notification = Notification(
        type=type,
        title=title,
        body=body,
        target_type=target_type,
        target_value=target_value,
        action_data=action_data,
        priority=priority,
        scheduled_at=scheduled_at,
        expiry_at=expiry_at,
        status=NotificationStatus.PENDING.value,
    )
    session.add(notification)
    await session.flush()
    await session.refresh(notification)

    logger.info(
        "notification_created",
        notification_id=str(notification.id),
        type=type,
        target=f"{target_type}:{target_value}",
        scheduled_at=scheduled_at.isoformat(),
    )

    return notification


# ===================================================================
# Internal API (used by processor)
# ===================================================================


async def resolve_notification(
    notification: Notification,
    session: AsyncSession,
    *,
    default_channel: str = DeliveryChannel.TELEGRAM.value,
) -> list[NotificationDelivery]:
    """Resolve notification target into individual delivery rows.

    Expands target_type:target_value into per-user deliveries.
    Does NOT commit (processor manages the transaction).

    Args:
        notification: The notification to resolve.
        session: Database session.
        default_channel: Channel for new deliveries.

    Returns:
        List of created NotificationDelivery objects.
    """
    user_ids = await _resolve_target_users(
        target_type=notification.target_type,
        target_value=notification.target_value,
        session=session,
    )

    if not user_ids:
        logger.warning(
            "notification_no_recipients",
            notification_id=str(notification.id),
            target=f"{notification.target_type}:{notification.target_value}",
        )
        return []

    deliveries = []
    for user_id in user_ids:
        delivery = NotificationDelivery(
            notification_id=notification.id,
            user_id=user_id,
            channel=default_channel,
            status=DeliveryStatus.PENDING.value,
        )
        session.add(delivery)
        deliveries.append(delivery)

    await session.flush()

    logger.info(
        "notification_resolved",
        notification_id=str(notification.id),
        delivery_count=len(deliveries),
        target=f"{notification.target_type}:{notification.target_value}",
    )

    return deliveries


# ===================================================================
# Target resolution helpers
# ===================================================================


async def _resolve_target_users(
    *,
    target_type: str,
    target_value: str,
    session: AsyncSession,
) -> list[UUID]:
    """Resolve a target specification into a list of user UUIDs."""

    if target_type == TargetType.USER.value:
        # Single user by UUID.
        try:
            user_id = UUID(target_value)
        except ValueError:
            logger.error(
                "notification_invalid_user_target",
                target_value=target_value,
            )
            return []
        # Verify user exists and is active.
        stmt = select(User.id).where(
            User.id == user_id,
            User.is_active.is_(True),
        )
        result = await session.execute(stmt)
        uid = result.scalar_one_or_none()
        return [uid] if uid else []

    if target_type == TargetType.PRACTICE.value:
        # All users with confirmed/attended bookings for this practice.
        try:
            practice_id = UUID(target_value)
        except ValueError:
            logger.error(
                "notification_invalid_practice_target",
                target_value=target_value,
            )
            return []
        stmt = (
            select(Booking.user_id)
            .where(
                Booking.practice_id == practice_id,
                Booking.status.in_([
                    BookingStatus.CONFIRMED.value,
                    BookingStatus.ATTENDED.value,
                ]),
            )
            .distinct()
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    if target_type == TargetType.ROLE.value:
        # All active users with a specific role.
        # PERF-04 TODO: Add LIMIT/pagination when user base grows.
        # Currently loads all matching user IDs into memory. For a
        # small user base this is fine, but at scale (10k+ users per
        # role) this should be converted to batched processing:
        #   - Add LIMIT/OFFSET loop here, or
        #   - Resolve in chunks in the processor stage, or
        #   - Use server-side cursor (stream_scalars).
        stmt = select(User.id).where(
            User.role == target_value,
            User.is_active.is_(True),
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    if target_type == TargetType.ALL.value:
        # All active users.
        # PERF-04 TODO: Add LIMIT/pagination when user base grows.
        # Same concern as ROLE above -- loads all user IDs at once.
        # At scale, switch to batched delivery creation to avoid
        # large in-memory lists and long-running transactions.
        stmt = select(User.id).where(User.is_active.is_(True))
        result = await session.execute(stmt)
        return list(result.scalars().all())

    logger.error(
        "notification_unknown_target_type",
        target_type=target_type,
    )
    return []
