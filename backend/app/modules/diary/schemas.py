# =============================================================================
# VELO Backend -- Diary Schemas (Phase 8.1: Check-ins)
# =============================================================================
#
# REQUEST:
#   CheckinRequest -- mood (required), comment (optional, max 1000 chars).
#
# RESPONSE:
#   CheckinResponse -- full checkin data.
#   PaginatedCheckinsResponse -- paginated list for GET /users/me/checkins.
#
# VALIDATION:
#   mood: must be one of low/mid/high (Literal, not free-form string).
#   comment: max 1000 chars (from config, enforced here as schema default).
# =============================================================================

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


# ===================================================================
# Request
# ===================================================================


class CheckinRequest(BaseModel):
    """POST /api/v1/practices/{id}/checkin body."""

    mood: Literal["low", "mid", "high"]
    comment: str | None = Field(default=None, max_length=1000)


# ===================================================================
# Response
# ===================================================================


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
