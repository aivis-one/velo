# =============================================================================
# VELO Backend -- Diary Schemas (Phase 8.1-8.4, NO-LITERALS)
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
# INSIGHTS (master-facing):
#   MoodDistribution / RatingDistribution / PracticeInsightsResponse
#
# SUGGESTION-6 fix: ConfigDict(from_attributes=True) instead of dict style.
# NO-LITERALS: all allowed values and field limits sourced from config.py:
#   settings.diary_allowed_moods       -- mood field values
#   settings.diary_allowed_ratings     -- rating field values
#   settings.diary_comment_max_length  -- comment field limit
#   settings.diary_entry_content_max_length
#   settings.diary_entry_title_max_length
#
# CR-01: MoodDistribution / RatingDistribution fields changed from
#   optional (default=0) to required. These are response-only schemas --
#   the service always provides concrete values. Removing defaults makes
#   OpenAPI mark them as required, so the TS generator emits non-optional
#   fields and frontend code doesn't need `?.` guards.
# =============================================================================

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.config import settings


# ===================================================================
# Check-in schemas (Phase 8.1)
# ===================================================================


class CheckinRequest(BaseModel):
    """POST /api/v1/practices/{id}/checkin body."""

    mood: str
    comment: str | None = Field(
        default=None,
        min_length=1,
        max_length=settings.diary_comment_max_length,
    )

    @field_validator("mood")
    @classmethod
    def mood_must_be_valid(cls, v: str) -> str:
        """Validate mood against allowed values from config."""
        allowed = settings.diary_allowed_moods
        if v not in allowed:
            raise ValueError(f"mood must be one of {allowed}, got '{v}'")
        return v


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

    rating: str
    comment: str | None = Field(
        default=None,
        min_length=1,
        max_length=settings.diary_comment_max_length,
    )

    @field_validator("rating")
    @classmethod
    def rating_must_be_valid(cls, v: str) -> str:
        """Validate rating against allowed values from config."""
        allowed = settings.diary_allowed_ratings
        if v not in allowed:
            raise ValueError(f"rating must be one of {allowed}, got '{v}'")
        return v


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

    content: str = Field(
        min_length=1, max_length=settings.diary_entry_content_max_length,
    )
    title: str | None = Field(
        default=None, max_length=settings.diary_entry_title_max_length,
    )
    mood: str | None = None
    practice_id: UUID | None = None

    @field_validator("mood")
    @classmethod
    def mood_must_be_valid(cls, v: str | None) -> str | None:
        """Validate mood against allowed values from config."""
        if v is None:
            return v
        allowed = settings.diary_allowed_moods
        if v not in allowed:
            raise ValueError(f"mood must be one of {allowed}, got '{v}'")
        return v


class UpdateDiaryEntryRequest(BaseModel):
    """PATCH /api/v1/diary/{id} body.

    All fields optional. Only provided fields are updated.
    """

    content: str | None = Field(
        default=None,
        min_length=1,
        max_length=settings.diary_entry_content_max_length,
    )
    title: str | None = Field(
        default=None, max_length=settings.diary_entry_title_max_length,
    )
    mood: str | None = None
    practice_id: UUID | None = None
    # Sentinel to distinguish "not provided" from "set to null".
    # If clear_mood is True, mood is set to None even if mood field is absent.
    clear_mood: bool = False
    clear_title: bool = False
    clear_practice: bool = False

    @field_validator("mood")
    @classmethod
    def mood_must_be_valid(cls, v: str | None) -> str | None:
        """Validate mood against allowed values from config."""
        if v is None:
            return v
        allowed = settings.diary_allowed_moods
        if v not in allowed:
            raise ValueError(f"mood must be one of {allowed}, got '{v}'")
        return v


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


# ===================================================================
# Practice Insights schemas (Phase 8.4, master-facing)
# ===================================================================


class MoodDistribution(BaseModel):
    """Check-in mood counts for a practice.

    CR-01: fields are required (no default=0). This is a response-only
    schema -- the service always provides concrete values. Making them
    required ensures OpenAPI marks them as such, and the TS generator
    emits non-optional fields.
    """

    high: int
    mid: int
    low: int


class RatingDistribution(BaseModel):
    """Feedback rating counts for a practice.

    CR-01: fields are required (no default=0). Same rationale as
    MoodDistribution above.
    """

    fire: int
    good: int
    confused: int


class PracticeInsightsResponse(BaseModel):
    """GET /api/v1/practices/{id}/insights -- aggregated data.

    All data is anonymous: no user IDs, names, or comment texts.
    Only numeric distributions and counts.
    """

    practice_id: UUID
    participants: int
    checkins: MoodDistribution
    feedbacks: RatingDistribution
    comments_count: int
