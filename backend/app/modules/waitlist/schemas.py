# =============================================================================
# VELO Backend -- Waitlist Schemas (Phase 5.3 + Frontend Backlog)
# =============================================================================
#
# WaitlistEntryResponse:            Base waitlist entry representation.
# WaitlistConfirmResponse:          Entry + new booking id after confirm.
# WaitlistWithPracticeResponse:     Entry + PracticeSummary (for list views).
# PaginatedWaitlistResponse:        Paginated list of WaitlistWithPractice.
# =============================================================================

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.modules.practices.schemas import PracticeSummary


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


# -- Frontend Backlog: Enriched waitlist schemas ---------------------------


class WaitlistWithPracticeResponse(BaseModel):
    """Waitlist entry with lightweight practice summary for list views.

    Used by GET /api/v1/waitlist/me. Gives the frontend enough data
    for card rendering (title, time, type, master) without N+1 calls.
    """

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
    practice: PracticeSummary

    model_config = {"from_attributes": True}


class PaginatedWaitlistResponse(BaseModel):
    """GET /api/v1/waitlist/me -- paginated list."""

    items: list[WaitlistWithPracticeResponse]
    total: int
    limit: int
    offset: int
