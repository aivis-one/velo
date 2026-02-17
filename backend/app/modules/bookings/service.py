# =============================================================================
# VELO Backend -- Booking Service (Phase 5.1+5.2+5.3+5.4, updated Phase 6.5)
# =============================================================================
#
# Business logic for booking create, cancel, attendance, and finalize.
#
# STATE MACHINE:
#   pending   -> confirmed, cancelled
#   confirmed -> attended, no_show, cancelled
#   attended  -> (terminal)
#   no_show   -> (terminal)
#   cancelled -> (terminal)
#
# ATTENDANCE (Phase 5.4):
#   join_booking:  sets joined_at (status stays confirmed)
#   leave_booking: sets left_at (requires joined_at)
#   finalize:      confirmed + joined_at -> attended
#                  confirmed + no joined_at -> no_show
#                  practice -> completed
#
# PURCHASE INTEGRATION (Phase 6.4):
#   create_booking: creates Purchase + double-entry ledger (always, even free)
#   finalize:       finalizes Purchases (unfreeze + commission)
#
# CANCELLATION POLICY (Phase 6.5):
#   cancel_booking now handles refunds based on deadline:
#     > cancellation_deadline_hours before practice -> 100% refund
#     <= cancellation_deadline_hours before practice -> 0% refund (early finalize)
#   Both paths produce double-entry ledger entries (even for free practices).
#
# CAPACITY:
#   Checked via COUNT of active bookings, not current_participants (TD-034).
#
# WAITLIST INTEGRATION (Phase 5.3):
#   After cancelling a booking, process_waitlist is called.
#
# SESSION RULES:
#   No session.commit() here (P-01). Router handles flush + refresh.
# =============================================================================

from datetime import datetime, timedelta, timezone
from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import (
    BadRequestError,
    ConflictError,
    NotFoundError,
)
from app.modules.bookings.models import Booking, BookingStatus
from app.modules.payments.purchase import (
    create_purchase_for_booking,
    finalize_purchases,
)
from app.modules.payments.refund import (
    early_finalize_booking,
    refund_booking,
)
from app.modules.practices.models import Practice, PracticeStatus
from app.modules.users.models import User

logger = structlog.get_logger()

# Statuses that count toward capacity.
_ACTIVE_BOOKING_STATUSES = {
    BookingStatus.PENDING.value,
    BookingStatus.CONFIRMED.value,
}

# Statuses from which cancellation is allowed.
_CANCELLABLE_STATUSES = {
    BookingStatus.PENDING.value,
    BookingStatus.CONFIRMED.value,
}

# Practice statuses that allow user check-in.
_JOINABLE_PRACTICE_STATUSES = {
    PracticeStatus.SCHEDULED.value,
    PracticeStatus.LIVE.value,
}

# Practice statuses that allow finalization.
_FINALIZABLE_PRACTICE_STATUSES = {
    PracticeStatus.SCHEDULED.value,
    PracticeStatus.LIVE.value,
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


async def create_booking(
    user: User,
    practice_id: UUID,
    session: AsyncSession,
) -> Booking:
    """Book a user into a practice.

    Validates:
    - Practice exists and is scheduled.
    - User is not the practice owner.
    - User has sufficient balance for paid practices.
    - Capacity not exceeded (if max_participants set).
    - No duplicate booking.

    Free practices are auto-confirmed (pending -> confirmed).
    Creates a Purchase with double-entry ledger (always, even free).
    """
    # Load practice with FOR UPDATE (capacity check + booking
    # must be atomic to prevent overbooking).
    stmt = (
        select(Practice)
        .where(Practice.id == practice_id)
        .with_for_update()
    )
    result = await session.execute(stmt)
    practice = result.scalar_one_or_none()

    if not practice:
        raise NotFoundError("Practice not found")

    # Only scheduled practices accept bookings.
    if practice.status != PracticeStatus.SCHEDULED.value:
        raise BadRequestError(
            "Can only book scheduled practices"
        )

    # Cannot book own practice.
    if practice.master_id == user.id:
        raise BadRequestError(
            "Cannot book your own practice"
        )

    # Check capacity.
    if practice.max_participants is not None:
        active_count = await _get_active_booking_count(
            session, practice_id,
        )
        if active_count >= practice.max_participants:
            raise BadRequestError("Practice is full")

    # Create booking (auto-confirm for free practices).
    booking = Booking(
        practice_id=practice_id,
        user_id=user.id,
        status=BookingStatus.CONFIRMED.value,
    )
    session.add(booking)

    # Flush to trigger UniqueConstraint check (P-05).
    try:
        async with session.begin_nested():
            await session.flush()
    except IntegrityError:
        raise ConflictError(
            "Already booked for this practice"
        ) from None

    # Double-entry purchase (always, even for free practices).
    purchase = await create_purchase_for_booking(
        booking=booking,
        practice=practice,
        user=user,
        session=session,
    )

    logger.info(
        "booking_created",
        booking_id=str(booking.id),
        purchase_id=str(purchase.id),
        practice_id=str(practice_id),
        user_id=str(user.id),
        status=booking.status,
        paid_cents=purchase.paid_cents,
    )

    return booking


async def cancel_booking(
    booking_id: UUID,
    user: User,
    session: AsyncSession,
    reason: str | None = None,
) -> Booking:
    """Cancel a booking with refund policy enforcement.

    Only the booking owner can cancel. Only pending/confirmed
    bookings can be cancelled.

    Refund policy (Phase 6.5):
    - Cancel > cancellation_deadline_hours before practice:
      100% refund (Purchase -> REFUNDED).
    - Cancel <= cancellation_deadline_hours before practice:
      0% refund, early finalize (Purchase -> COMPLETED,
      master keeps money minus commission).

    Both paths create double-entry ledger entries, even for
    free practices (zero-amount entries as proof of path).

    After cancellation, triggers waitlist processing to notify
    the next waiting user (Phase 5.3).

    Uses FOR UPDATE to prevent concurrent cancellation (P-12).
    """
    stmt = (
        select(Booking)
        .where(Booking.id == booking_id)
        .with_for_update()
    )
    result = await session.execute(stmt)
    booking = result.scalar_one_or_none()

    if not booking:
        raise NotFoundError("Booking not found")

    # P-08: 404 not 403 to avoid revealing booking existence.
    if booking.user_id != user.id:
        raise NotFoundError("Booking not found")

    if booking.status not in _CANCELLABLE_STATUSES:
        raise BadRequestError(
            f"Cannot cancel booking in status "
            f"{booking.status}"
        )

    booking.status = BookingStatus.CANCELLED.value
    booking.cancelled_at = datetime.now(timezone.utc)
    booking.cancellation_reason = reason

    # Phase 6.5: Refund or early-finalize based on deadline.
    # Load practice for scheduled_at (read-only, no FOR UPDATE needed).
    practice_stmt = (
        select(Practice)
        .where(Practice.id == booking.practice_id)
    )
    practice = (
        await session.execute(practice_stmt)
    ).scalar_one()

    deadline = practice.scheduled_at - timedelta(
        hours=settings.cancellation_deadline_hours,
    )
    now = datetime.now(timezone.utc)

    if now < deadline:
        # Early cancel: full refund.
        await refund_booking(
            booking=booking,
            practice=practice,
            session=session,
        )
        logger.info(
            "booking_cancelled_with_refund",
            booking_id=str(booking_id),
            user_id=str(user.id),
            reason=reason,
        )
    else:
        # Late cancel: master keeps the money (early finalize).
        await early_finalize_booking(
            booking=booking,
            practice=practice,
            session=session,
        )
        logger.info(
            "booking_cancelled_no_refund",
            booking_id=str(booking_id),
            user_id=str(user.id),
            reason=reason,
        )

    # Phase 5.3: Notify next waiting user in the queue.
    from app.modules.waitlist.service import process_waitlist
    await process_waitlist(booking.practice_id, session)

    return booking


# ===================================================================
# Phase 5.4: Attendance
# ===================================================================


async def join_booking(
    booking_id: UUID,
    user: User,
    session: AsyncSession,
) -> Booking:
    """Mark user as joined (check-in).

    Sets joined_at timestamp. Status stays confirmed -- the
    transition to attended happens at finalize.

    Validates:
    - Booking exists and belongs to user (P-08).
    - Status is confirmed.
    - Practice is in joinable state (scheduled/live).
    - Not already joined (409).

    Uses FOR UPDATE (P-12).
    """
    stmt = (
        select(Booking)
        .where(Booking.id == booking_id)
        .with_for_update()
    )
    result = await session.execute(stmt)
    booking = result.scalar_one_or_none()

    if not booking:
        raise NotFoundError("Booking not found")

    if booking.user_id != user.id:
        raise NotFoundError("Booking not found")

    if booking.status != BookingStatus.CONFIRMED.value:
        raise BadRequestError(
            "Can only join a confirmed booking"
        )

    if booking.joined_at is not None:
        raise ConflictError("Already joined")

    # Check practice is in joinable state.
    practice_stmt = (
        select(Practice)
        .where(Practice.id == booking.practice_id)
    )
    practice = (
        await session.execute(practice_stmt)
    ).scalar_one()

    if practice.status not in _JOINABLE_PRACTICE_STATUSES:
        raise BadRequestError("Cannot join this practice")

    booking.joined_at = datetime.now(timezone.utc)

    logger.info(
        "booking_joined",
        booking_id=str(booking_id),
        user_id=str(user.id),
        practice_id=str(booking.practice_id),
    )

    return booking


async def leave_booking(
    booking_id: UUID,
    user: User,
    session: AsyncSession,
) -> Booking:
    """Mark user as left.

    Sets left_at timestamp. Requires joined_at to be set.

    Validates:
    - Booking exists and belongs to user (P-08).
    - joined_at is set (400 if not).
    - left_at is not already set (409).

    Uses FOR UPDATE (P-12).
    """
    stmt = (
        select(Booking)
        .where(Booking.id == booking_id)
        .with_for_update()
    )
    result = await session.execute(stmt)
    booking = result.scalar_one_or_none()

    if not booking:
        raise NotFoundError("Booking not found")

    if booking.user_id != user.id:
        raise NotFoundError("Booking not found")

    if booking.joined_at is None:
        raise BadRequestError(
            "Cannot leave without joining first"
        )

    if booking.left_at is not None:
        raise ConflictError("Already left")

    booking.left_at = datetime.now(timezone.utc)

    logger.info(
        "booking_left",
        booking_id=str(booking_id),
        user_id=str(user.id),
        practice_id=str(booking.practice_id),
    )

    return booking


async def finalize_practice(
    practice_id: UUID,
    user: User,
    session: AsyncSession,
) -> Practice:
    """Finalize a practice -- set attendance statuses + financial settlement.

    Master-only. Transitions:
    - confirmed + joined_at IS NOT NULL -> attended
    - confirmed + joined_at IS NULL     -> no_show
    - Practice status -> completed
    - All pending purchases -> completed (unfreeze + commission)

    Validates:
    - Practice exists and belongs to master (P-08: 404).
    - Practice is in finalizable state (scheduled/live).

    Uses FOR UPDATE on practice (P-12).
    """
    stmt = (
        select(Practice)
        .where(Practice.id == practice_id)
        .with_for_update()
    )
    result = await session.execute(stmt)
    practice = result.scalar_one_or_none()

    if not practice:
        raise NotFoundError("Practice not found")

    # P-08: 404 not 403 for non-owner.
    if practice.master_id != user.id:
        raise NotFoundError("Practice not found")

    if practice.status not in _FINALIZABLE_PRACTICE_STATUSES:
        raise BadRequestError("Practice already finalized")

    # Bulk update: confirmed + joined -> attended, else -> no_show.
    bookings_stmt = (
        select(Booking)
        .where(
            Booking.practice_id == practice_id,
            Booking.status == BookingStatus.CONFIRMED.value,
        )
        .with_for_update()
    )
    bookings_result = await session.execute(bookings_stmt)
    bookings = bookings_result.scalars().all()

    attended_count = 0
    no_show_count = 0

    for booking in bookings:
        if booking.joined_at is not None:
            booking.status = BookingStatus.ATTENDED.value
            attended_count += 1
        else:
            booking.status = BookingStatus.NO_SHOW.value
            no_show_count += 1

    practice.status = PracticeStatus.COMPLETED.value

    # Finalize all purchases: unfreeze + commission (double-entry).
    finalized = await finalize_purchases(
        practice_id=practice_id,
        practice=practice,
        session=session,
    )

    logger.info(
        "practice_finalized",
        practice_id=str(practice_id),
        master_id=str(user.id),
        attended=attended_count,
        no_show=no_show_count,
        purchases_finalized=len(finalized),
    )

    return practice


async def get_attendance(
    practice_id: UUID,
    user: User,
    session: AsyncSession,
) -> tuple[Practice, list[Booking]]:
    """Get attendance list for a practice (master-only).

    Returns all non-cancelled bookings with attendance data.

    Validates:
    - Practice exists and belongs to master (P-08: 404).
    """
    stmt = select(Practice).where(Practice.id == practice_id)
    result = await session.execute(stmt)
    practice = result.scalar_one_or_none()

    if not practice:
        raise NotFoundError("Practice not found")

    if practice.master_id != user.id:
        raise NotFoundError("Practice not found")

    bookings_stmt = (
        select(Booking)
        .where(
            Booking.practice_id == practice_id,
            Booking.status != BookingStatus.CANCELLED.value,
        )
        .order_by(Booking.created_at)
    )
    bookings_result = await session.execute(bookings_stmt)
    bookings = list(bookings_result.scalars().all())

    return practice, bookings
