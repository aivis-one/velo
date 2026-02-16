# =============================================================================
# VELO Backend -- Booking Router (Phase 5.2 + 5.4)
# =============================================================================
#
# ENDPOINTS:
#   POST   /api/v1/bookings              -- create booking
#   DELETE /api/v1/bookings/{id}         -- cancel booking
#   POST   /api/v1/bookings/{id}/join    -- check-in (Phase 5.4)
#   POST   /api/v1/bookings/{id}/leave   -- check-out (Phase 5.4)
#   POST   /api/v1/practices/{id}/finalize   -- finalize (Phase 5.4)
#   GET    /api/v1/practices/{id}/attendance  -- attendance list (Phase 5.4)
#
# AUTH: get_current_user on booking endpoints.
#       get_current_master on practice-level endpoints.
# SESSION: Mutating = get_db_session. Read = get_db_reader.
# =============================================================================

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_reader, get_db_session
from app.modules.auth.dependencies import (
    get_current_master,
    get_current_user,
)
from app.modules.bookings.models import BookingStatus
from app.modules.bookings.schemas import (
    AttendanceItemResponse,
    AttendanceResponse,
    BookingResponse,
    CancelBookingRequest,
    CreateBookingRequest,
)
from app.modules.bookings.service import (
    cancel_booking,
    create_booking,
    finalize_practice,
    get_attendance,
    join_booking,
    leave_booking,
)
from app.modules.masters.models import MasterProfile
from app.modules.practices.schemas import PracticeResponse
from app.modules.users.models import User

router = APIRouter(
    prefix="/api/v1/bookings", tags=["bookings"],
)

# Separate router for practice-level attendance endpoints.
practices_attendance_router = APIRouter(
    prefix="/api/v1/practices", tags=["attendance"],
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
    await session.flush()
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
    """Cancel a booking (owner only)."""
    reason = body.reason if body else None
    booking = await cancel_booking(
        booking_id, user, session, reason=reason,
    )
    await session.flush()
    await session.refresh(booking)
    return BookingResponse.model_validate(booking)


# ===================================================================
# Phase 5.4: Attendance (booking-level)
# ===================================================================


@router.post(
    "/{booking_id}/join",
    response_model=BookingResponse,
)
async def join_booking_endpoint(
    booking_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> BookingResponse:
    """Check in to a practice (sets joined_at)."""
    booking = await join_booking(booking_id, user, session)
    await session.flush()
    await session.refresh(booking)
    return BookingResponse.model_validate(booking)


@router.post(
    "/{booking_id}/leave",
    response_model=BookingResponse,
)
async def leave_booking_endpoint(
    booking_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> BookingResponse:
    """Check out from a practice (sets left_at)."""
    booking = await leave_booking(booking_id, user, session)
    await session.flush()
    await session.refresh(booking)
    return BookingResponse.model_validate(booking)


# ===================================================================
# Phase 5.4: Attendance (practice-level, master-only)
# ===================================================================


@practices_attendance_router.post(
    "/{practice_id}/finalize",
    response_model=PracticeResponse,
)
async def finalize_practice_endpoint(
    practice_id: UUID,
    master_tuple: tuple[User, MasterProfile] = Depends(
        get_current_master,
    ),
    session: AsyncSession = Depends(get_db_session),
) -> PracticeResponse:
    """Finalize a practice (master only).

    Sets attended/no_show on bookings, practice -> completed.
    """
    user, _profile = master_tuple
    practice = await finalize_practice(
        practice_id, user, session,
    )
    await session.flush()
    await session.refresh(practice)
    return PracticeResponse.model_validate(practice)


@practices_attendance_router.get(
    "/{practice_id}/attendance",
    response_model=AttendanceResponse,
)
async def get_attendance_endpoint(
    practice_id: UUID,
    master_tuple: tuple[User, MasterProfile] = Depends(
        get_current_master,
    ),
    session: AsyncSession = Depends(get_db_reader),
) -> AttendanceResponse:
    """Get attendance list for a practice (master only)."""
    user, _profile = master_tuple
    practice, bookings = await get_attendance(
        practice_id, user, session,
    )

    items = [
        AttendanceItemResponse(
            booking_id=b.id,
            user_id=b.user_id,
            status=b.status,
            joined_at=b.joined_at,
            left_at=b.left_at,
        )
        for b in bookings
    ]

    return AttendanceResponse(
        practice_id=practice.id,
        total=len(items),
        attended=sum(
            1 for b in bookings
            if b.status == BookingStatus.ATTENDED.value
        ),
        no_show=sum(
            1 for b in bookings
            if b.status == BookingStatus.NO_SHOW.value
        ),
        pending=sum(
            1 for b in bookings
            if b.status in {
                BookingStatus.PENDING.value,
                BookingStatus.CONFIRMED.value,
            }
        ),
        items=items,
    )
