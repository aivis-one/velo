# =============================================================================
# VELO Backend -- Diary Schemas (Phase 8.1-8.3)
# =============================================================================
#
# CHECKIN:
#   CheckinRequest / CheckinResponse / PaginatedCheckinsResponse
#
# FEEDBACK:
#   FeedbackRequest / FeedbackResponse / PaginatedFeedbacksResponse
#
# DIARY ENTRY:
#   CreateDiaryEntryRequest / UpdateDiaryEntryRequest
#   DiaryEntryResponse / PaginatedDiaryEntriesResponse
#
# SUGGESTION-6 fix: ConfigDict(from_attributes=True) instead of dict style.
# =============================================================================

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


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

    model_config = ConfigDict(from_attributes=True)


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

    model_config = ConfigDict(from_attributes=True)


class PaginatedFeedbacksResponse(BaseModel):
    """GET /api/v1/users/me/feedbacks -- paginated list."""

    items: list[FeedbackResponse]
    total: int
    limit: int
    offset: int


# ===================================================================
# Diary Entry schemas (Phase 8.3)
# ===================================================================


class CreateDiaryEntryRequest(BaseModel):
    """POST /api/v1/diary body."""

    content: str = Field(min_length=1, max_length=10000)
    title: str | None = Field(default=None, max_length=200)
    mood: Literal["low", "mid", "high"] | None = None
    practice_id: UUID | None = None


class UpdateDiaryEntryRequest(BaseModel):
    """PATCH /api/v1/diary/{id} body.

    All fields optional. Only provided fields are updated.
    """

    content: str | None = Field(default=None, min_length=1, max_length=10000)
    title: str | None = Field(default=None, max_length=200)
    mood: Literal["low", "mid", "high"] | None = None
    practice_id: UUID | None = None
    # Sentinel to distinguish "not provided" from "set to null".
    # If clear_mood is True, mood is set to None even if mood field is absent.
    clear_mood: bool = False
    clear_title: bool = False
    clear_practice: bool = False


class DiaryEntryResponse(BaseModel):
    """Single diary entry in API responses."""

    id: UUID
    user_id: UUID
    practice_id: UUID | None
    title: str | None
    content: str
    mood: str | None
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class PaginatedDiaryEntriesResponse(BaseModel):
    """GET /api/v1/diary -- paginated list."""

    items: list[DiaryEntryResponse]
    total: int
    limit: int
    offset: int
