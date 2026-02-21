# =============================================================================
# VELO Backend -- Booking Router (Phase 5.2 + 5.4 + Backlog, updated 6.7)
# =============================================================================
#
# ENDPOINTS:
#   POST   /api/v1/bookings              -- create booking (+ optional promo)
#   GET    /api/v1/bookings/me           -- my bookings (Frontend Backlog)
#   GET    /api/v1/bookings/{id}         -- booking detail (Frontend Backlog)
#   DELETE /api/v1/bookings/{id}         -- cancel booking
#   POST   /api/v1/bookings/{id}/join    -- check-in (Phase 5.4)
#   POST   /api/v1/bookings/{id}/leave   -- check-out (Phase 5.4)
#   POST   /api/v1/practices/{id}/finalize   -- finalize (Phase 5.4)
#   GET    /api/v1/practices/{id}/attendance  -- attendance list (Phase 5.4)
#
# Phase 6.7 Batch 4: POST /bookings now accepts optional promo_code
# in CreateBookingRequest. Promo is validated before booking creation.
#
# ROUTE ORDER:
#   /me MUST come before /{booking_id} to avoid FastAPI parsing "me"
#   as a UUID path parameter.
#
# AUTH: get_current_user on booking endpoints.
#       get_current_master on practice-level endpoints.
# SESSION: Mutating = get_db_session. Read = get_db_reader.
# =============================================================================

from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_reader, get_db_session
from app.modules.auth.dependencies import (
    get_current_master,
    get_current_user,
)
from app.core.exceptions import NotFoundError
from app.modules.bookings.models import BookingStatus
from app.modules.bookings.schemas import (
    AttendanceItemResponse,
    AttendanceResponse,
    BookingDetailResponse,
    BookingResponse,
    BookingWithPracticeResponse,
    CancelBookingRequest,
    CreateBookingRequest,
    PaginatedBookingsResponse,
)
from app.modules.bookings.service import (
    cancel_booking,
    create_booking,
    finalize_practice,
    get_attendance,
    get_booking_by_id,
    join_booking,
    leave_booking,
    list_user_bookings,
)
from app.modules.masters.models import MasterProfile
from app.modules.practices.models import Practice
from app.modules.practices.schemas import PracticeSummary, PracticeResponse
from app.modules.promos.models import Promo
from app.modules.promos.validation import validate_promo
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
    """Book the current user into a practice.

    Phase 6.7: optional promo_code in body for discount.
    """
    # Validate promo if provided.
    promo: Promo | None = None
    if body.promo_code:
        practice = await session.get(Practice, body.practice_id)
        if not practice:
            raise NotFoundError("Practice not found")
        promo = await validate_promo(
            code=body.promo_code,
            practice=practice,
            user_id=user.id,
            session=session,
        )

    booking = await create_booking(
        user, body.practice_id, session, promo=promo,
    )
    await session.flush()
    await session.refresh(booking)
    return BookingResponse.model_validate(booking)


# ===================================================================
# Frontend Backlog: GET /me -- my bookings (BEFORE /{booking_id})
# ===================================================================


@router.get(
    "/me",
    response_model=PaginatedBookingsResponse,
)
async def list_my_bookings_endpoint(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_reader),
    status_filter: Literal[
        "pending", "confirmed", "cancelled",
        "attended", "no_show",
    ] | None = Query(
        default=None, alias="status",
    ),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> PaginatedBookingsResponse:
    """List bookings for the current user.

    Returns paginated list with embedded PracticeSummary so the
    frontend can render cards without additional API calls.

    Optional ``status`` filter (e.g. ``?status=confirmed``).
    """
    items, total = await list_user_bookings(
        user, session,
        status_filter=status_filter,
        limit=limit,
        offset=offset,
    )

    return PaginatedBookingsResponse(
        items=[
            BookingWithPracticeResponse(
                id=booking.id,
                practice_id=booking.practice_id,
                user_id=booking.user_id,
                status=booking.status,
                purchase_id=booking.purchase_id,
                cancelled_at=booking.cancelled_at,
                cancellation_reason=booking.cancellation_reason,
                joined_at=booking.joined_at,
                left_at=booking.left_at,
                created_at=booking.created_at,
                updated_at=booking.updated_at,
                practice=PracticeSummary.model_validate(practice),
            )
            for booking, practice in items
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


# ===================================================================
# Frontend Backlog: GET /{booking_id} -- booking detail
# ===================================================================


@router.get(
    "/{booking_id}",
    response_model=BookingDetailResponse,
)
async def get_booking_detail_endpoint(
    booking_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_reader),
) -> BookingDetailResponse:
    """Get a single booking with full practice details.

    Access control:
      - Booking owner (deep link from notification).
      - Master of the practice (attendance dashboard).

    Returns 404 for non-existent or unauthorized bookings (P-08).
    """
    booking, practice = await get_booking_by_id(
        booking_id, user, session,
    )

    return BookingDetailResponse(
        id=booking.id,
        practice_id=booking.practice_id,
        user_id=booking.user_id,
        status=booking.status,
        purchase_id=booking.purchase_id,
        cancelled_at=booking.cancelled_at,
        cancellation_reason=booking.cancellation_reason,
        joined_at=booking.joined_at,
        left_at=booking.left_at,
        created_at=booking.created_at,
        updated_at=booking.updated_at,
        practice=PracticeResponse.model_validate(practice),
    )


# ===================================================================
# DELETE /{booking_id} -- cancel booking
# ===================================================================


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
# Phase 5.4: Attendance (practice-level)
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
    """Finalize a practice -- resolve attendance + financial settlement."""
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
    """Get attendance list for a practice (master-only)."""
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

    attended = sum(1 for b in bookings if b.status == BookingStatus.ATTENDED.value)
    no_show = sum(1 for b in bookings if b.status == BookingStatus.NO_SHOW.value)
    pending = sum(
        1 for b in bookings
        if b.status in {BookingStatus.PENDING.value, BookingStatus.CONFIRMED.value}
    )

    return AttendanceResponse(
        practice_id=practice.id,
        total=len(bookings),
        attended=attended,
        no_show=no_show,
        pending=pending,
        items=items,
    )
