# =============================================================================
# VELO Backend -- Booking Router (Phase 5.2)
# =============================================================================
#
# ENDPOINTS:
#   POST   /api/v1/bookings          -- create booking
#   DELETE /api/v1/bookings/{id}     -- cancel booking
#
# AUTH: get_current_user on both endpoints.
# SESSION: Both mutating -- get_db_session (write).
# =============================================================================

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.modules.auth.dependencies import get_current_user
from app.modules.bookings.schemas import (
    BookingResponse,
    CancelBookingRequest,
    CreateBookingRequest,
)
from app.modules.bookings.service import (
    cancel_booking,
    create_booking,
)
from app.modules.users.models import User

router = APIRouter(
    prefix="/api/v1/bookings", tags=["bookings"],
)


@router.post(
    "",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_booking_endpoint(
    body: CreateBookingRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> BookingResponse:
    """Book the current user into a practice."""
    booking = await create_booking(
        user, body.practice_id, session,
    )
    await session.refresh(booking)
    return BookingResponse.model_validate(booking)


@router.delete(
    "/{booking_id}",
    response_model=BookingResponse,
)
async def cancel_booking_endpoint(
    booking_id: UUID,
    body: CancelBookingRequest | None = None,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> BookingResponse:
    """Cancel a booking (owner only).

    No refund logic -- stub until Phase 6.
    """
    reason = body.reason if body else None
    booking = await cancel_booking(
        booking_id, user, session, reason=reason,
    )
    await session.flush()
    await session.refresh(booking)
    return BookingResponse.model_validate(booking)
