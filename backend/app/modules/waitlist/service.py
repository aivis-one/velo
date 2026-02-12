# =============================================================================
# VELO Backend -- Waitlist Service (Phase 5.3)
# =============================================================================
#
# Business logic for waitlist join, leave/decline, confirm, and
# automatic processing when a booking is cancelled.
#
# JOIN FLOW:
#   1. FOR UPDATE on practice (same lock as booking -- prevents races)
#   2. Validate: exists, scheduled, IS full, no active booking, not owner
#   3. Check existing waitlist entry:
#      - active (waiting/notified) -> 409
#      - rejoinable (left/declined/expired) -> UPDATE (re-join, new position)
#      - none -> INSERT with position = MAX+1 subquery
#   4. IntegrityError -> rollback + 409 (P-05)
#
# LEAVE/DECLINE FLOW:
#   1. FOR UPDATE on waitlist entry (P-12)
#   2. Owner check (P-08: 404 not 403)
#   3. waiting -> left; notified -> declined
#   4. If declined (was notified): process_waitlist -> notify next
#
# CONFIRM FLOW:
#   1. FOR UPDATE on waitlist entry (P-12)
#   2. Owner check, status must be notified, not expired
#   3. Create booking (skip capacity check -- spot is reserved)
#   4. status -> converted
#
# PROCESS_WAITLIST (internal):
#   Called from cancel_booking and leave/decline.
#   Finds first waiting entry, transitions to notified,
#   sets expires_at = now + 30 min. Stub notification log.
#
# SESSION RULES:
#   No session.commit() here (P-01). Router calls flush + refresh.
# =============================================================================

from datetime import UTC, datetime, timedelta
from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    BadRequestError,
    ConflictError,
    NotFoundError,
)
from app.modules.bookings.models import Booking, BookingStatus
from app.modules.practices.models import Practice, PracticeStatus
from app.modules.users.models import User
from app.modules.waitlist.models import (
    ACTIVE_STATUSES,
    REJOINABLE_STATUSES,
    Waitlist,
    WaitlistStatus,
)

logger = structlog.get_logger()

# How long a notified user has to confirm.
_CONFIRM_WINDOW = timedelta(minutes=30)

# Booking statuses that count toward capacity (same as bookings/service.py).
_ACTIVE_BOOKING_STATUSES = {
    BookingStatus.PENDING.value,
    BookingStatus.CONFIRMED.value,
}


async def _get_active_booking_count(
    session: AsyncSession,
    practice_id: UUID,
) -> int:
    """Count active bookings for a practice (TD-034)."""
    stmt = (
        select(func.count(Booking.id))
        .where(
            Booking.practice_id == practice_id,
            Booking.status.in_(_ACTIVE_BOOKING_STATUSES),
        )
    )
    result = await session.execute(stmt)
    return result.scalar_one()


async def _next_position_subquery(practice_id: UUID) -> int:
    """Build a scalar subquery for next position in waitlist.

    Returns a correlated subquery: COALESCE(MAX(position), 0) + 1
    filtered by practice_id.
    """
    return (
        select(func.coalesce(func.max(Waitlist.position), 0) + 1)
        .where(Waitlist.practice_id == practice_id)
        .scalar_subquery()
    )


async def join_waitlist(
    user: User,
    practice_id: UUID,
    session: AsyncSession,
) -> Waitlist:
    """Add user to the waitlist for a full practice.

    Validates:
    - Practice exists and is scheduled.
    - Practice IS full (otherwise user should book directly).
    - User is not the practice owner.
    - No active booking for this practice.
    - No active waitlist entry (waiting/notified).
    - Rejoinable entry (left/declined/expired) -> re-join with new position.
    """
    # Lock practice (same strategy as create_booking).
    stmt = (
        select(Practice)
        .where(Practice.id == practice_id)
        .with_for_update()
    )
    result = await session.execute(stmt)
    practice = result.scalar_one_or_none()

    if not practice:
        raise NotFoundError("Practice not found")

    if practice.status != PracticeStatus.SCHEDULED.value:
        raise BadRequestError("Can only join waitlist for scheduled practices")

    if practice.master_id == user.id:
        raise BadRequestError("Cannot join waitlist for your own practice")

    # Practice must be full -- otherwise user should book directly.
    if practice.max_participants is None:
        raise BadRequestError(
            "Practice has no capacity limit -- book directly"
        )

    active_count = await _get_active_booking_count(session, practice_id)
    if active_count < practice.max_participants:
        raise BadRequestError("Practice is not full -- book directly")

    # Check no active booking exists.
    booking_stmt = (
        select(func.count(Booking.id))
        .where(
            Booking.practice_id == practice_id,
            Booking.user_id == user.id,
            Booking.status.in_(_ACTIVE_BOOKING_STATUSES),
        )
    )
    booking_result = await session.execute(booking_stmt)
    if booking_result.scalar_one() > 0:
        raise ConflictError("Already booked for this practice")

    # Check existing waitlist entry.
    existing_stmt = (
        select(Waitlist)
        .where(
            Waitlist.practice_id == practice_id,
            Waitlist.user_id == user.id,
        )
        .with_for_update()
    )
    existing_result = await session.execute(existing_stmt)
    existing = existing_result.scalar_one_or_none()

    now = datetime.now(UTC)
    next_pos = await _next_position_subquery(practice_id)

    if existing:
        if existing.status in ACTIVE_STATUSES:
            raise ConflictError("Already on waitlist for this practice")

        if existing.status in REJOINABLE_STATUSES:
            # Re-join: update existing row with new position.
            existing.status = WaitlistStatus.WAITING.value
            existing.position = next_pos
            existing.joined_at = now
            existing.notified_at = None
            existing.expires_at = None

            await session.flush()
            await session.refresh(existing)

            logger.info(
                "waitlist_rejoined",
                waitlist_id=str(existing.id),
                practice_id=str(practice_id),
                user_id=str(user.id),
                position=existing.position,
            )
            return existing

    # New entry.
    entry = Waitlist(
        practice_id=practice_id,
        user_id=user.id,
        position=next_pos,
        status=WaitlistStatus.WAITING.value,
        joined_at=now,
    )
    session.add(entry)

    try:
        await session.flush()
    except IntegrityError:
        await session.rollback()
        raise ConflictError(
            "Already on waitlist for this practice"
        ) from None

    await session.refresh(entry)

    logger.info(
        "waitlist_joined",
        waitlist_id=str(entry.id),
        practice_id=str(practice_id),
        user_id=str(user.id),
        position=entry.position,
    )

    return entry


async def leave_waitlist(
    waitlist_id: UUID,
    user: User,
    session: AsyncSession,
) -> Waitlist:
    """Leave the waitlist or decline a notification.

    - waiting -> left
    - notified -> declined (triggers process_waitlist for next user)

    Uses FOR UPDATE (P-12).
    """
    stmt = (
        select(Waitlist)
        .where(Waitlist.id == waitlist_id)
        .with_for_update()
    )
    result = await session.execute(stmt)
    entry = result.scalar_one_or_none()

    if not entry:
        raise NotFoundError("Waitlist entry not found")

    # P-08: 404 not 403 for non-owner.
    if entry.user_id != user.id:
        raise NotFoundError("Waitlist entry not found")

    was_notified = entry.status == WaitlistStatus.NOTIFIED.value

    if entry.status == WaitlistStatus.WAITING.value:
        entry.status = WaitlistStatus.LEFT.value
    elif entry.status == WaitlistStatus.NOTIFIED.value:
        entry.status = WaitlistStatus.DECLINED.value
    else:
        raise BadRequestError("Cannot leave waitlist in current status")

    logger.info(
        "waitlist_left",
        waitlist_id=str(waitlist_id),
        user_id=str(user.id),
        new_status=entry.status,
    )

    # If user was notified (had a spot offer), notify next in line.
    if was_notified:
        await process_waitlist(entry.practice_id, session)

    return entry


async def confirm_waitlist(
    waitlist_id: UUID,
    user: User,
    session: AsyncSession,
) -> tuple[Waitlist, Booking]:
    """Confirm a waitlist spot -- creates a booking.

    Only works when status=notified and expires_at > now().
    Creates a booking (confirmed) and transitions to converted.

    Returns (waitlist_entry, booking).
    """
    stmt = (
        select(Waitlist)
        .where(Waitlist.id == waitlist_id)
        .with_for_update()
    )
    result = await session.execute(stmt)
    entry = result.scalar_one_or_none()

    if not entry:
        raise NotFoundError("Waitlist entry not found")

    # P-08: 404 not 403 for non-owner.
    if entry.user_id != user.id:
        raise NotFoundError("Waitlist entry not found")

    if entry.status != WaitlistStatus.NOTIFIED.value:
        raise BadRequestError("Can only confirm a notified waitlist entry")

    # Lazy expiration check.
    now = datetime.now(UTC)
    if entry.expires_at and entry.expires_at < now:
        entry.status = WaitlistStatus.EXPIRED.value
        # Notify next in line since this one expired.
        await process_waitlist(entry.practice_id, session)
        raise BadRequestError("Waitlist offer has expired")

    # Create booking (auto-confirmed, skip capacity check --
    # spot was reserved when previous booking was cancelled).
    booking = Booking(
        practice_id=entry.practice_id,
        user_id=user.id,
        status=BookingStatus.CONFIRMED.value,
    )
    session.add(booking)

    try:
        await session.flush()
    except IntegrityError:
        await session.rollback()
        raise ConflictError(
            "Already booked for this practice"
        ) from None

    entry.status = WaitlistStatus.CONVERTED.value

    logger.info(
        "waitlist_confirmed",
        waitlist_id=str(waitlist_id),
        booking_id=str(booking.id),
        practice_id=str(entry.practice_id),
        user_id=str(user.id),
    )

    return entry, booking


async def process_waitlist(
    practice_id: UUID,
    session: AsyncSession,
) -> Waitlist | None:
    """Notify the next waiting user in the queue.

    Called automatically when:
    - A booking is cancelled (from cancel_booking)
    - A notified user declines or expires

    Finds the first 'waiting' entry by position, transitions
    to 'notified', and sets expires_at.

    Returns the notified entry, or None if queue is empty.
    """
    stmt = (
        select(Waitlist)
        .where(
            Waitlist.practice_id == practice_id,
            Waitlist.status == WaitlistStatus.WAITING.value,
        )
        .order_by(Waitlist.position)
        .limit(1)
        .with_for_update()
    )
    result = await session.execute(stmt)
    entry = result.scalar_one_or_none()

    if not entry:
        logger.info(
            "waitlist_empty",
            practice_id=str(practice_id),
        )
        return None

    now = datetime.now(UTC)
    entry.status = WaitlistStatus.NOTIFIED.value
    entry.notified_at = now
    entry.expires_at = now + _CONFIRM_WINDOW

    # Stub notification -- real implementation in Phase 7.
    logger.info(
        "waitlist_notification_stub",
        waitlist_id=str(entry.id),
        practice_id=str(practice_id),
        user_id=str(entry.user_id),
        expires_at=entry.expires_at.isoformat(),
        message="TODO: Send Telegram notification to user",
    )

    return entry
