# =============================================================================
# VELO Backend -- Booking Schemas (Phase 5.2 + 5.4 + Backlog, updated 6.7)
# =============================================================================
#
# BookingResponse:                Base booking representation.
# BookingWithPracticeResponse:    Booking + PracticeSummary (for list views).
# BookingDetailResponse:          Booking + full PracticeResponse (for detail).
# PaginatedBookingsResponse:      Paginated list of BookingWithPractice items.
# AttendanceItemResponse:         Single booking in attendance list (Phase 5.4).
# AttendanceResponse:             Full attendance summary (Phase 5.4).
#
# Phase 6.7 Batch 4: CreateBookingRequest gains optional promo_code.
#
# CR-01: Response schemas use BookingStatus StrEnum instead of str
#   so OpenAPI emits enum values and generated TypeScript types
#   produce union literals instead of plain string.
# =============================================================================

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.bookings.models import BookingStatus
from app.modules.practices.schemas import PracticeSummary, PracticeResponse


class CreateBookingRequest(BaseModel):
    """POST /api/v1/bookings -- request body.

    Phase 6.7: optional promo_code for discount.
    Existing clients that omit promo_code continue to work unchanged.
    """

    practice_id: UUID
    promo_code: str | None = Field(
        default=None,
        min_length=1, max_length=50,
        description="Optional promo code to apply.",
    )


class CancelBookingRequest(BaseModel):
    """DELETE /api/v1/bookings/{id} -- optional body."""

    reason: str | None = Field(
        default=None, max_length=1000,
    )


class BookingResponse(BaseModel):
    """Booking representation returned by endpoints."""

    id: UUID
    practice_id: UUID
    user_id: UUID
    status: BookingStatus
    purchase_id: UUID | None
    cancelled_at: datetime | None
    cancellation_reason: str | None
    joined_at: datetime | None
    left_at: datetime | None
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}


# -- Frontend Backlog: Enriched booking schemas ----------------------------


class BookingWithPracticeResponse(BaseModel):
    """Booking with lightweight practice summary for list views.

    Used by GET /api/v1/bookings/me. Gives the frontend enough data
    for card rendering (title, time, type, master) without N+1 calls.
    """

    id: UUID
    practice_id: UUID
    user_id: UUID
    status: BookingStatus
    purchase_id: UUID | None
    cancelled_at: datetime | None
    cancellation_reason: str | None
    joined_at: datetime | None
    left_at: datetime | None
    created_at: datetime
    updated_at: datetime | None
    practice: PracticeSummary

    model_config = {"from_attributes": True}


class BookingDetailResponse(BaseModel):
    """Booking with full practice details for single-booking view.

    Used by GET /api/v1/bookings/{id}. Returns the complete
    PracticeResponse so the frontend can render a full detail page
    (deep link from notification, master dashboard, etc.).
    """

    id: UUID
    practice_id: UUID
    user_id: UUID
    status: BookingStatus
    purchase_id: UUID | None
    cancelled_at: datetime | None
    cancellation_reason: str | None
    joined_at: datetime | None
    left_at: datetime | None
    created_at: datetime
    updated_at: datetime | None
    practice: PracticeResponse

    model_config = {"from_attributes": True}


class PaginatedBookingsResponse(BaseModel):
    """GET /api/v1/bookings/me -- paginated list."""

    items: list[BookingWithPracticeResponse]
    total: int
    limit: int
    offset: int


# -- Phase 5.4: Attendance --


class AttendanceItemResponse(BaseModel):
    """Single booking in attendance list."""

    booking_id: UUID
    user_id: UUID
    status: BookingStatus
    joined_at: datetime | None
    left_at: datetime | None

    model_config = {"from_attributes": True}


class AttendanceResponse(BaseModel):
    """GET /api/v1/practices/{id}/attendance -- response."""

    practice_id: UUID
    total: int
    attended: int
    no_show: int
    pending: int
    items: list[AttendanceItemResponse]
