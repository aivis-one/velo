# =============================================================================
# VELO Backend -- Practice Schemas (Phase 4.2 + 4.3/4.4 + Frontend Backlog)
# =============================================================================
#
# VALIDATION:
#   - scheduled_at must be in the future
#   - timezone must be a valid IANA timezone
#   - duration_minutes must be within config bounds
#   - practice_type validated via Literal
#
# PRICING VALIDATION (Phase 4.3/4.4):
#   - is_free=True  -> price_cents forced to 0 in service
#   - is_free=False -> price_cents must be > 0 (validated in service)
#   - currency validated via Literal (EUR only for MVP)
#
# PRACTICE SUMMARY (Frontend Backlog A-03):
#   Lightweight practice representation for embedding in booking /
#   waitlist / purchase responses. Contains only the fields needed
#   for list-view cards (title, type, time, duration, master).
#
# MASTER_NAME (Frontend F3 prep):
#   master_name added to PracticeResponse and PracticeSummary.
#   Populated via JOIN with users table in service layer.
#   Default None for backward compatibility with model_validate()
#   on raw Practice ORM objects (e.g. in booking/waitlist schemas).
#
# P-02 NOTE:
#   NOT NULL fields are typed as `X | None` in UpdatePracticeRequest
#   so that "not sent" works with exclude_unset. The service layer
#   guards against explicit null.
# =============================================================================

from datetime import datetime, timezone
from typing import Literal
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, Field, field_validator

from app.core.config import settings


class CreatePracticeRequest(BaseModel):
    """POST /api/v1/practices -- request body."""

    practice_type: Literal["live", "series", "one_on_one", "replay"]
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    scheduled_at: datetime
    duration_minutes: int
    timezone: str = Field(max_length=50)
    max_participants: int | None = Field(
        default=None, ge=1, le=10000,
    )
    zoom_link: str | None = Field(default=None, max_length=500)
    parent_practice_id: UUID | None = None

    # -- Pricing (Phase 4.3/4.4) --
    is_free: bool = True
    price_cents: int = Field(default=0, ge=0)
    currency: Literal["EUR"] = "EUR"

    @field_validator("scheduled_at")
    @classmethod
    def scheduled_at_must_be_future(
        cls, v: datetime,
    ) -> datetime:
        """Reject practices scheduled in the past."""
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        if v <= datetime.now(timezone.utc):
            raise ValueError("scheduled_at must be in the future")
        return v

    @field_validator("timezone")
    @classmethod
    def timezone_must_be_iana(cls, v: str) -> str:
        """Validate timezone is a real IANA timezone."""
        try:
            ZoneInfo(v)
        except (ZoneInfoNotFoundError, KeyError):
            raise ValueError(
                f"Invalid IANA timezone: {v}"
            ) from None
        return v

    @field_validator("duration_minutes")
    @classmethod
    def duration_in_range(cls, v: int) -> int:
        """Validate duration is within configured bounds."""
        mn = settings.practice_min_duration_minutes
        mx = settings.practice_max_duration_minutes
        if v < mn or v > mx:
            raise ValueError(
                f"duration_minutes must be between {mn} and {mx}"
            )
        return v


class UpdatePracticeRequest(BaseModel):
    """PATCH /api/v1/practices/{id} -- request body.

    All fields optional. Only provided fields are updated.
    NOT NULL columns use service-layer guard against explicit
    null (P-02). Status transitions are validated against the
    state machine in service.
    """

    title: str | None = Field(
        default=None, min_length=1, max_length=200,
    )
    description: str | None = Field(default=None, max_length=5000)
    scheduled_at: datetime | None = None
    duration_minutes: int | None = None
    timezone: str | None = Field(default=None, max_length=50)
    max_participants: int | None = Field(
        default=None, ge=1, le=10000,
    )
    zoom_link: str | None = Field(default=None, max_length=500)
    # I-04 fix: only statuses reachable via _VALID_TRANSITIONS in service.
    # "cancelled" removed -- only reachable via cancel_practice() (Phase 6.5).
    # "draft" removed -- nothing transitions TO draft.
    status: Literal[
        "scheduled", "live", "completed", "deleted",
    ] | None = None

    # -- Pricing (Phase 4.3/4.4) --
    is_free: bool | None = None
    price_cents: int | None = Field(default=None, ge=0)
    currency: Literal["EUR"] | None = None

    @field_validator("scheduled_at")
    @classmethod
    def scheduled_at_must_be_future(
        cls, v: datetime | None,
    ) -> datetime | None:
        """Reject practices scheduled in the past."""
        if v is None:
            return v
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        if v <= datetime.now(timezone.utc):
            raise ValueError("scheduled_at must be in the future")
        return v

    @field_validator("timezone")
    @classmethod
    def timezone_must_be_iana(
        cls, v: str | None,
    ) -> str | None:
        """Validate timezone is a real IANA timezone."""
        if v is None:
            return v
        try:
            ZoneInfo(v)
        except (ZoneInfoNotFoundError, KeyError):
            raise ValueError(
                f"Invalid IANA timezone: {v}"
            ) from None
        return v

    @field_validator("duration_minutes")
    @classmethod
    def duration_in_range(
        cls, v: int | None,
    ) -> int | None:
        """Validate duration is within configured bounds."""
        if v is None:
            return v
        mn = settings.practice_min_duration_minutes
        mx = settings.practice_max_duration_minutes
        if v < mn or v > mx:
            raise ValueError(
                f"duration_minutes must be between {mn} and {mx}"
            )
        return v


class PracticeResponse(BaseModel):
    """Practice representation returned by all endpoints."""

    id: UUID
    master_id: UUID
    master_name: str | None = None
    practice_type: str
    status: str
    title: str
    description: str | None
    scheduled_at: datetime
    duration_minutes: int
    timezone: str
    max_participants: int | None
    current_participants: int
    zoom_link: str | None
    parent_practice_id: UUID | None

    # -- Pricing --
    is_free: bool
    price_cents: int
    currency: str

    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class PaginatedPracticesResponse(BaseModel):
    """GET /api/v1/practices -- paginated public list."""

    items: list[PracticeResponse]
    total: int
    limit: int
    offset: int


# -- Frontend Backlog A-03: Lightweight practice summary -------------------


class PracticeSummary(BaseModel):
    """Compact practice representation for embedding in related responses.

    Used inside BookingWithPracticeResponse, WaitlistWithPracticeResponse,
    and PurchaseWithPracticeResponse to give the frontend enough data
    for list-view cards without a separate GET /practices/{id} call.
    """

    id: UUID
    title: str
    practice_type: str
    scheduled_at: datetime
    duration_minutes: int
    master_id: UUID
    master_name: str | None = None

    model_config = {"from_attributes": True}
