# =============================================================================
# VELO Backend -- Reminder Scheduling (Phase 7.4, QW-2/QW-3)
# =============================================================================
#
# Automatic reminders for upcoming practices. Creates Notification records
# with future scheduled_at -- the existing processor (Phase 7.2) picks
# them up when the time comes.
#
# USER REMINDERS (per booking):
#   3 notifications: 24h, 1h, 10min before practice.scheduled_at.
#   target_type=user, target_value=<user_id>.
#   Skipped if scheduled_at is already in the past (< now + 5min buffer).
#
# MASTER REMINDERS (per practice):
#   3 notifications: 24h, 1h, 10min before practice.scheduled_at.
#   target_type=user, target_value=<master_id>.
#   Scheduled when practice transitions to "scheduled" status.
#
# CANCELLATION:
#   cancel_reminders_for_booking: expire user reminders for one booking.
#   cancel_all_reminders_for_practice: expire ALL reminders (user + master).
#
# RESCHEDULING:
#   reschedule_reminders_for_practice: cancel all + re-create for all
#   active bookings + master. Called when scheduled_at changes.
#
# FILTERING:
#   Reminders are linked to a practice via action_data["practice_id"].
#   JSONB query: Notification.action_data["practice_id"].astext == str(id).
#
# QW-2/QW-3: schedule_reminders and schedule_master_reminders accept an
#   optional master_name keyword argument. When provided, the DB lookup
#   for display name is skipped. reschedule_reminders_for_practice fetches
#   the name once and passes it to all calls, eliminating N+1 queries.
#
# SESSION RULES:
#   No session.commit() here (P-01). Caller manages transaction.
# =============================================================================

from datetime import UTC, datetime, timedelta
from uuid import UUID

import structlog
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.bookings.models import Booking, BookingStatus
from app.modules.masters.models import MasterProfile
from app.modules.notifications.models import (
    Notification,
    NotificationStatus,
    NotificationType,
    TargetType,
)
from app.modules.notifications.service import create_notification
from app.modules.practices.models import Practice
from app.modules.users.models import User

logger = structlog.get_logger()

# Buffer: don't schedule a reminder if it's less than 5 minutes away.
_MIN_LEAD_TIME = timedelta(minutes=5)

# Priority for reminders (higher than default 5, lower than urgent 1).
_REMINDER_PRIORITY = 2

# Reminder types mapped to their lead time before practice start.
_USER_REMINDER_SPECS: list[tuple[str, timedelta]] = [
    (NotificationType.REMINDER_24H.value, timedelta(hours=24)),
    (NotificationType.REMINDER_1H.value, timedelta(hours=1)),
    (NotificationType.REMINDER_10MIN.value, timedelta(minutes=10)),
]

_MASTER_REMINDER_SPECS: list[tuple[str, timedelta]] = [
    (NotificationType.MASTER_REMINDER_24H.value, timedelta(hours=24)),
    (NotificationType.MASTER_REMINDER_1H.value, timedelta(hours=1)),
    (NotificationType.MASTER_REMINDER_10MIN.value, timedelta(minutes=10)),
]

# All reminder types (user + master) for bulk queries.
_ALL_USER_REMINDER_TYPES = {spec[0] for spec in _USER_REMINDER_SPECS}
_ALL_MASTER_REMINDER_TYPES = {spec[0] for spec in _MASTER_REMINDER_SPECS}
_ALL_REMINDER_TYPES = _ALL_USER_REMINDER_TYPES | _ALL_MASTER_REMINDER_TYPES


# ===================================================================
# Helper: get master display name
# ===================================================================


async def _get_master_display_name(
    master_id: UUID,
    session: AsyncSession,
) -> str:
    """Get master's display name for template variables.

    Checks MasterProfile.data.profile.display_name first,
    falls back to User.first_name, then "Master".
    """
    profile = await session.get(MasterProfile, master_id)
    if profile:
        display_name = (
            profile.data
            .get("profile", {})
            .get("display_name")
        )
        if display_name:
            return display_name

    user = await session.get(User, master_id)
    if user and user.first_name:
        return user.first_name

    return "Master"


# ===================================================================
# Helper: build action_data for templates + deep linking
# ===================================================================


def _build_action_data(
    practice: Practice,
    master_name: str,
    *,
    participants_count: int | None = None,
) -> dict:
    """Build action_data dict for reminder notifications.

    Contains both template variables and deep link intent.
    """
    data: dict = {
        "action": "open_practice",
        "params": {"practice_id": str(practice.id)},
        "practice_id": str(practice.id),
        "practice_title": practice.title,
        "scheduled_at": practice.scheduled_at.isoformat(),
        "master_name": master_name,
    }
    if participants_count is not None:
        data["participants_count"] = str(participants_count)
    return data


# ===================================================================
# Schedule user reminders (called from create_booking / confirm_waitlist)
# ===================================================================


async def schedule_reminders(
    booking: Booking,
    practice: Practice,
    user: User,
    session: AsyncSession,
    *,
    master_name: str | None = None,
) -> list[Notification]:
    """Schedule up to 3 reminder notifications for a booked user.

    Skips reminders whose send time is less than _MIN_LEAD_TIME away.
    expiry_at = practice.scheduled_at (no point sending after start).

    Args:
        booking: The confirmed booking.
        practice: The booked practice.
        user: The user who booked.
        session: Database session (caller manages commit).
        master_name: Pre-fetched display name (QW-3). If None, fetched
            from DB. Pass this when calling in a loop for the same
            practice to avoid redundant queries.

    Returns:
        List of created Notification objects (0-3).
    """
    now = datetime.now(UTC)
    cutoff = now + _MIN_LEAD_TIME
    created: list[Notification] = []

    # QW-3: reuse caller-provided name or fetch from DB.
    if master_name is None:
        master_name = await _get_master_display_name(
            practice.master_id, session,
        )
    action_data = _build_action_data(practice, master_name)

    for reminder_type, lead_time in _USER_REMINDER_SPECS:
        send_at = practice.scheduled_at - lead_time

        if send_at < cutoff:
            continue

        notification = await create_notification(
            type=reminder_type,
            title="Reminder",
            body="",
            target_type=TargetType.USER.value,
            target_value=str(user.id),
            session=session,
            action_data=action_data,
            priority=_REMINDER_PRIORITY,
            scheduled_at=send_at,
            expiry_at=practice.scheduled_at,
        )
        created.append(notification)

    if created:
        logger.info(
            "reminders_scheduled",
            booking_id=str(booking.id),
            practice_id=str(practice.id),
            user_id=str(user.id),
            count=len(created),
            types=[n.type for n in created],
        )

    return created


# ===================================================================
# Schedule master reminders (called when practice -> scheduled)
# ===================================================================


async def schedule_master_reminders(
    practice: Practice,
    session: AsyncSession,
    *,
    master_name: str | None = None,
) -> list[Notification]:
    """Schedule up to 3 reminder notifications for the practice master.

    Called when practice transitions to "scheduled" status.
    Skips reminders whose send time is less than _MIN_LEAD_TIME away.

    Args:
        practice: The practice that became scheduled.
        session: Database session (caller manages commit).
        master_name: Pre-fetched display name (QW-3). If None, fetched
            from DB. Useful when caller already resolved the name.

    Returns:
        List of created Notification objects (0-3).
    """
    now = datetime.now(UTC)
    cutoff = now + _MIN_LEAD_TIME
    created: list[Notification] = []

    # QW-3: reuse caller-provided name or fetch from DB.
    if master_name is None:
        master_name = await _get_master_display_name(
            practice.master_id, session,
        )

    # Count current active bookings for the template.
    count_stmt = (
        select(func.count(Booking.id))
        .where(
            Booking.practice_id == practice.id,
            Booking.status == BookingStatus.CONFIRMED.value,
        )
    )
    result = await session.execute(count_stmt)
    participants_count = result.scalar_one()

    action_data = _build_action_data(
        practice,
        master_name,
        participants_count=participants_count,
    )

    for reminder_type, lead_time in _MASTER_REMINDER_SPECS:
        send_at = practice.scheduled_at - lead_time

        if send_at < cutoff:
            continue

        notification = await create_notification(
            type=reminder_type,
            title="Reminder",
            body="",
            target_type=TargetType.USER.value,
            target_value=str(practice.master_id),
            session=session,
            action_data=action_data,
            priority=_REMINDER_PRIORITY,
            scheduled_at=send_at,
            expiry_at=practice.scheduled_at,
        )
        created.append(notification)

    if created:
        logger.info(
            "master_reminders_scheduled",
            practice_id=str(practice.id),
            master_id=str(practice.master_id),
            count=len(created),
            types=[n.type for n in created],
        )

    return created


# ===================================================================
# Cancel reminders for a single booking
# ===================================================================


async def cancel_reminders_for_booking(
    user_id: UUID,
    practice_id: UUID,
    session: AsyncSession,
) -> int:
    """Cancel pending user reminders for a specific booking.

    Marks PENDING reminder notifications as EXPIRED where:
    - type is a user reminder (REMINDER_24H/1H/10MIN)
    - target is this specific user
    - action_data.practice_id matches

    Does NOT touch master reminders.

    Returns count of expired notifications.
    """
    stmt = (
        update(Notification)
        .where(
            Notification.type.in_(_ALL_USER_REMINDER_TYPES),
            Notification.status == NotificationStatus.PENDING.value,
            Notification.target_type == TargetType.USER.value,
            Notification.target_value == str(user_id),
            Notification.action_data["practice_id"].astext == str(practice_id),
        )
        .values(status=NotificationStatus.EXPIRED.value)
    )
    result = await session.execute(stmt)
    count = result.rowcount

    if count > 0:
        logger.info(
            "reminders_cancelled_for_booking",
            user_id=str(user_id),
            practice_id=str(practice_id),
            expired_count=count,
        )

    return count


# ===================================================================
# Cancel ALL reminders for a practice (user + master)
# ===================================================================


async def cancel_all_reminders_for_practice(
    practice_id: UUID,
    session: AsyncSession,
) -> int:
    """Cancel all pending reminders for a practice.

    Expires both user and master reminders. Used when:
    - Master cancels the practice (cancel_practice).
    - Before rescheduling (reschedule_reminders_for_practice).

    Returns count of expired notifications.
    """
    stmt = (
        update(Notification)
        .where(
            Notification.type.in_(_ALL_REMINDER_TYPES),
            Notification.status == NotificationStatus.PENDING.value,
            Notification.action_data["practice_id"].astext == str(practice_id),
        )
        .values(status=NotificationStatus.EXPIRED.value)
    )
    result = await session.execute(stmt)
    count = result.rowcount

    if count > 0:
        logger.info(
            "all_reminders_cancelled_for_practice",
            practice_id=str(practice_id),
            expired_count=count,
        )

    return count


# ===================================================================
# Reschedule all reminders (when scheduled_at changes)
# ===================================================================


async def reschedule_reminders_for_practice(
    practice: Practice,
    session: AsyncSession,
) -> int:
    """Cancel and re-create all reminders for a practice.

    Called when master updates practice.scheduled_at.
    Steps:
    1. Cancel all existing reminders (user + master).
    2. Re-schedule master reminders.
    3. Re-schedule user reminders for each active booking.

    QW-3: Fetches master display name once and passes it to all
    schedule_* calls, avoiding N+1 queries (was 1 per booking + 1
    for master = N+2 total; now exactly 1).

    Returns total count of new reminders created.
    """
    # Step 1: Cancel all existing.
    await cancel_all_reminders_for_practice(practice.id, session)

    total_created = 0

    # QW-3: Fetch master name ONCE for all reminders.
    master_name = await _get_master_display_name(
        practice.master_id, session,
    )

    # Step 2: Re-schedule master reminders.
    master_reminders = await schedule_master_reminders(
        practice, session, master_name=master_name,
    )
    total_created += len(master_reminders)

    # Step 3: Re-schedule user reminders for active bookings.
    bookings_stmt = (
        select(Booking)
        .where(
            Booking.practice_id == practice.id,
            Booking.status.in_({
                BookingStatus.CONFIRMED.value,
            }),
        )
    )
    result = await session.execute(bookings_stmt)
    bookings = result.scalars().all()

    for booking in bookings:
        user = await session.get(User, booking.user_id)
        if not user:
            continue

        reminders = await schedule_reminders(
            booking, practice, user, session,
            master_name=master_name,
        )
        total_created += len(reminders)

    logger.info(
        "reminders_rescheduled",
        practice_id=str(practice.id),
        active_bookings=len(bookings),
        total_reminders_created=total_created,
    )

    return total_created