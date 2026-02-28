# =============================================================================
# VELO Backend -- Diary Schemas (Phase 8.1: Check-ins, Phase 8.2: Feedbacks)
# =============================================================================
#
# CHECKIN:
#   CheckinRequest  -- mood (required), comment (optional, max 1000 chars).
#   CheckinResponse -- full checkin data.
#   PaginatedCheckinsResponse -- paginated list.
#
# FEEDBACK:
#   FeedbackRequest  -- rating (required), comment (optional, max 1000 chars).
#   FeedbackResponse -- full feedback data.
#   PaginatedFeedbacksResponse -- paginated list.
#
# VALIDATION:
#   mood:    must be one of low/mid/high (Literal).
#   rating:  must be one of fire/good/confused (Literal).
#   comment: max 1000 chars (from config).
# =============================================================================

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


# ===================================================================
# Check-in schemas (Phase 8.1)
# ===================================================================


class CheckinRequest(BaseModel):
    """POST /api/v1/practices/{id}/checkin body."""

    mood: Literal["low", "mid", "high"]
    comment: str | None = Field(default=None, max_length=1000)


class CheckinResponse(BaseModel):
    """Single checkin in API responses."""

    id: UUID
    practice_id: UUID
    user_id: UUID
    booking_id: UUID
    mood: str
    comment: str | None
    check_type: str
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class PaginatedCheckinsResponse(BaseModel):
    """GET /api/v1/users/me/checkins -- paginated list."""

    items: list[CheckinResponse]
    total: int
    limit: int
    offset: int


# ===================================================================
# Feedback schemas (Phase 8.2)
# ===================================================================


class FeedbackRequest(BaseModel):
    """POST /api/v1/practices/{id}/feedback body."""

    rating: Literal["fire", "good", "confused"]
    comment: str | None = Field(default=None, max_length=1000)


class FeedbackResponse(BaseModel):
    """Single feedback in API responses."""

    id: UUID
    practice_id: UUID
    user_id: UUID
    booking_id: UUID
    rating: str
    comment: str | None
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class PaginatedFeedbacksResponse(BaseModel):
    """GET /api/v1/users/me/feedbacks -- paginated list."""

    items: list[FeedbackResponse]
    total: int
    limit: int
    offset: int
