# =============================================================================
# VELO Backend -- Booking Schemas (Phase 5.2)
# =============================================================================

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CreateBookingRequest(BaseModel):
    """POST /api/v1/bookings -- request body."""

    practice_id: UUID


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
    status: str
    purchase_id: UUID | None
    cancelled_at: datetime | None
    cancellation_reason: str | None
    joined_at: datetime | None
    left_at: datetime | None
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}
