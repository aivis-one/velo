# =============================================================================
# VELO Backend -- Waitlist Schemas (Phase 5.3)
# =============================================================================

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class WaitlistEntryResponse(BaseModel):
    """Waitlist entry returned by all endpoints."""

    id: UUID
    practice_id: UUID
    user_id: UUID
    position: int
    status: str
    joined_at: datetime
    notified_at: datetime | None
    expires_at: datetime | None
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class WaitlistConfirmResponse(BaseModel):
    """Response from POST /waitlist/{id}/confirm.

    Returns both the converted waitlist entry and the new booking id.
    """

    waitlist_entry: WaitlistEntryResponse
    booking_id: UUID
