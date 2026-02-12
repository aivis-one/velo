# =============================================================================
# VELO Backend -- Booking Service (Phase 5.1+5.2)
# =============================================================================
#
# Business logic for booking create and cancel.
#
# STATE MACHINE:
#   pending   -> confirmed, cancelled
#   confirmed -> attended, no_show, cancelled
#   attended  -> (terminal)
#   no_show   -> (terminal)
#   cancelled -> (terminal)
#
# CAPACITY:
#   Checked via COUNT of active bookings, not current_participants (TD-034).
#
# PAID PRACTICES:
#   Blocked with 400 "Payment required" until Phase 6.
#
# DUPLICATE BOOKINGS:
#   UniqueConstraint (practice_id, user_id). IntegrityError -> 409.
#
# SESSION RULES:
#   No session.commit() here (P-01). Router handles flush + refresh.
# =============================================================================

from datetime import datetime, timezone
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
    - Practice is free (paid blocked until Phase 6).
    - Capacity not exceeded (if max_participants set).
    - No duplicate booking.

    Free practices are auto-confirmed (pending -> confirmed).
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

    # Paid practices blocked until Phase 6.
    if not practice.is_free:
        raise BadRequestError(
            "Payment required for paid practices"
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
        await session.flush()
    except IntegrityError:
        await session.rollback()
        raise ConflictError(
            "Already booked for this practice"
        ) from None

    logger.info(
        "booking_created",
        booking_id=str(booking.id),
        practice_id=str(practice_id),
        user_id=str(user.id),
        status=booking.status,
    )

    return booking


async def cancel_booking(
    booking_id: UUID,
    user: User,
    session: AsyncSession,
    reason: str | None = None,
) -> Booking:
    """Cancel a booking.

    Only the booking owner can cancel. Only pending/confirmed
    bookings can be cancelled. No refund logic (stub until Phase 6).

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

    logger.info(
        "booking_cancelled",
        booking_id=str(booking_id),
        user_id=str(user.id),
        reason=reason,
    )

    return booking
