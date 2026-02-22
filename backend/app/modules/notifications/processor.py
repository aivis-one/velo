# =============================================================================
# VELO Backend -- Notification Processor (Phase 7.2)
# =============================================================================
#
# Background asyncio.Task that runs inside FastAPI lifespan.
# Two-stage pipeline:
#
# STAGE 1 — RESOLUTION:
#   Poll notifications WHERE status=pending AND scheduled_at <= now().
#   For each: check expiry, resolve target into deliveries, set processing.
#
# STAGE 2 — DELIVERY:
#   Poll deliveries WHERE status=pending AND attempts < max.
#   For each: send via channel formatter, update status/attempts/error.
#
# ROLLUP:
#   After delivery batch, check if all deliveries for a notification are
#   terminal (sent/failed). Update notification status accordingly:
#     any sent → notification=sent
#     all failed → notification=failed
#
# BACKOFF:
#   Empty poll → interval doubles (up to max_backoff).
#   Found work → interval resets to base.
#
# SESSION MANAGEMENT:
#   Processor runs outside request context. Uses get_session_factory()
#   to create sessions manually, same pattern as webhook_router.
#
# DEPLOYMENT:
#   MVP: background task in FastAPI lifespan (Phase 7.2).
#   Future: separate Docker service with own entrypoint (Phase 9+).
#
# ERROR HANDLING:
#   Each notification/delivery is processed independently. One failure
#   does not block others. Unhandled exceptions in the main loop are
#   caught, logged, and the loop continues after backoff.
# =============================================================================

import asyncio
from datetime import UTC, datetime

import structlog
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_session_factory
from app.modules.notifications.formatters import get_formatter
from app.modules.notifications.models import (
    DeliveryStatus,
    Notification,
    NotificationDelivery,
    NotificationStatus,
)
from app.modules.notifications.service import resolve_notification
from app.modules.users.models import User

logger = structlog.get_logger()

# Batch size for polling queries.
_BATCH_SIZE = 50


# ===================================================================
# Main loop
# ===================================================================


async def run_processor() -> None:
    """Main processor loop. Runs until cancelled.

    Called from FastAPI lifespan as a background task.
    Catches all exceptions to prevent the loop from dying.
    """
    interval = settings.notification_poll_interval_seconds
    base_interval = settings.notification_poll_interval_seconds
    max_backoff = settings.notification_max_backoff_seconds

    logger.info(
        "notification_processor_started",
        poll_interval=base_interval,
        max_backoff=max_backoff,
        max_attempts=settings.notification_max_delivery_attempts,
    )

    while True:
        try:
            work_done = await _poll_cycle()

            if work_done:
                interval = base_interval
            else:
                interval = min(interval * 2, max_backoff)

        except asyncio.CancelledError:
            logger.info("notification_processor_stopped")
            return
        except Exception:
            logger.exception("notification_processor_error")
            interval = max_backoff

        try:
            await asyncio.sleep(interval)
        except asyncio.CancelledError:
            logger.info("notification_processor_stopped")
            return


# ===================================================================
# Poll cycle
# ===================================================================


async def _poll_cycle() -> bool:
    """Run one poll cycle: resolve + deliver + rollup.

    Returns True if any work was done (resets backoff).
    """
    work_done = False

    # Stage 1: Resolve pending notifications into deliveries.
    resolved = await _stage_resolve()
    if resolved > 0:
        work_done = True

    # Stage 2: Deliver pending deliveries.
    delivered = await _stage_deliver()
    if delivered > 0:
        work_done = True

    # Stage 3: Rollup notification statuses.
    if work_done:
        await _stage_rollup()

    return work_done


# ===================================================================
# Stage 1: Resolution
# ===================================================================


async def _stage_resolve() -> int:
    """Poll pending notifications and resolve targets into deliveries.

    Returns count of notifications resolved.
    """
    factory = get_session_factory()
    session = factory()
    resolved_count = 0

    try:
        now = datetime.now(UTC)

        # Fetch pending notifications ready to send.
        stmt = (
            select(Notification)
            .where(
                Notification.status == NotificationStatus.PENDING.value,
                Notification.scheduled_at <= now,
            )
            .order_by(
                Notification.priority.asc(),
                Notification.scheduled_at.asc(),
            )
            .limit(_BATCH_SIZE)
            .with_for_update(skip_locked=True)
        )
        result = await session.execute(stmt)
        notifications = list(result.scalars().all())

        if not notifications:
            return 0

        for notification in notifications:
            # Check expiry.
            if notification.expiry_at and now > notification.expiry_at:
                notification.status = NotificationStatus.EXPIRED.value
                logger.info(
                    "notification_expired",
                    notification_id=str(notification.id),
                    type=notification.type,
                    expiry_at=notification.expiry_at.isoformat(),
                )
                continue

            # Set processing.
            notification.status = NotificationStatus.PROCESSING.value

            # Resolve target into deliveries.
            deliveries = await resolve_notification(
                notification, session,
            )

            if not deliveries:
                # No recipients — mark as sent (nothing to do).
                notification.status = NotificationStatus.SENT.value
                logger.info(
                    "notification_sent_no_recipients",
                    notification_id=str(notification.id),
                )
            else:
                resolved_count += 1

        await session.commit()

    except Exception:
        await session.rollback()
        logger.exception("notification_resolve_error")
    finally:
        await session.close()

    if resolved_count > 0:
        logger.info(
            "notification_resolve_batch",
            resolved=resolved_count,
        )

    return resolved_count


# ===================================================================
# Stage 2: Delivery
# ===================================================================


async def _stage_deliver() -> int:
    """Poll pending deliveries and send via channel formatters.

    Returns count of deliveries attempted.
    """
    factory = get_session_factory()
    session = factory()
    delivered_count = 0
    max_attempts = settings.notification_max_delivery_attempts

    try:
        # Fetch pending deliveries with room for retry.
        stmt = (
            select(NotificationDelivery, Notification, User)
            .join(
                Notification,
                NotificationDelivery.notification_id == Notification.id,
            )
            .join(
                User,
                NotificationDelivery.user_id == User.id,
            )
            .where(
                NotificationDelivery.status == DeliveryStatus.PENDING.value,
                NotificationDelivery.attempts < max_attempts,
            )
            .order_by(NotificationDelivery.created_at.asc())
            .limit(_BATCH_SIZE)
            .with_for_update(
                skip_locked=True,
                of=NotificationDelivery,
            )
        )
        result = await session.execute(stmt)
        rows = list(result.all())

        if not rows:
            return 0

        for delivery, notification, user in rows:
            delivered_count += 1

            formatter = get_formatter(delivery.channel)
            deep_link = formatter.format_deep_link(
                notification.action_data,
            )

            try:
                send_result = await formatter.send(
                    title=notification.title,
                    body=notification.body,
                    user_telegram_id=user.telegram_id,
                    deep_link=deep_link,
                    channel_options=delivery.channel_options,
                )
            except Exception as exc:
                # Formatter raised — treat as failure.
                send_result = None
                delivery.attempts += 1
                delivery.error_message = str(exc)[:500]

                if delivery.attempts >= max_attempts:
                    delivery.status = DeliveryStatus.FAILED.value

                logger.warning(
                    "notification_delivery_exception",
                    delivery_id=str(delivery.id),
                    channel=delivery.channel,
                    attempts=delivery.attempts,
                    error=str(exc)[:200],
                )
                continue

            delivery.attempts += 1

            if send_result.success:
                delivery.status = DeliveryStatus.SENT.value
                delivery.sent_at = datetime.now(UTC)
                logger.debug(
                    "notification_delivery_sent",
                    delivery_id=str(delivery.id),
                    user_id=str(delivery.user_id),
                    channel=delivery.channel,
                )
            else:
                delivery.error_message = (
                    send_result.error_message or "Unknown error"
                )[:500]

                if delivery.attempts >= max_attempts:
                    delivery.status = DeliveryStatus.FAILED.value
                    logger.warning(
                        "notification_delivery_failed_final",
                        delivery_id=str(delivery.id),
                        attempts=delivery.attempts,
                        error=delivery.error_message,
                    )
                else:
                    logger.info(
                        "notification_delivery_retry",
                        delivery_id=str(delivery.id),
                        attempts=delivery.attempts,
                        max_attempts=max_attempts,
                        error=delivery.error_message,
                    )

        await session.commit()

    except Exception:
        await session.rollback()
        logger.exception("notification_deliver_error")
    finally:
        await session.close()

    if delivered_count > 0:
        logger.info(
            "notification_deliver_batch",
            attempted=delivered_count,
        )

    return delivered_count


# ===================================================================
# Stage 3: Rollup
# ===================================================================


async def _stage_rollup() -> None:
    """Update notification status based on delivery results.

    For each notification in 'processing' status:
      - If no pending deliveries remain:
        - Any sent → notification=sent
        - All failed → notification=failed
    """
    factory = get_session_factory()
    session = factory()

    try:
        # Find processing notifications with no pending deliveries left.
        pending_count_subq = (
            select(func.count(NotificationDelivery.id))
            .where(
                NotificationDelivery.notification_id == Notification.id,
                NotificationDelivery.status == DeliveryStatus.PENDING.value,
            )
            .correlate(Notification)
            .scalar_subquery()
        )

        stmt = (
            select(Notification)
            .where(
                Notification.status == NotificationStatus.PROCESSING.value,
                pending_count_subq == 0,
            )
            .with_for_update(skip_locked=True)
        )
        result = await session.execute(stmt)
        notifications = list(result.scalars().all())

        for notification in notifications:
            # Count sent deliveries.
            sent_stmt = (
                select(func.count(NotificationDelivery.id))
                .where(
                    NotificationDelivery.notification_id == notification.id,
                    NotificationDelivery.status == DeliveryStatus.SENT.value,
                )
            )
            sent_count = (await session.execute(sent_stmt)).scalar_one()

            if sent_count > 0:
                notification.status = NotificationStatus.SENT.value
            else:
                notification.status = NotificationStatus.FAILED.value

            logger.info(
                "notification_rollup",
                notification_id=str(notification.id),
                new_status=notification.status,
                sent_deliveries=sent_count,
            )

        if notifications:
            await session.commit()

    except Exception:
        await session.rollback()
        logger.exception("notification_rollup_error")
    finally:
        await session.close()
