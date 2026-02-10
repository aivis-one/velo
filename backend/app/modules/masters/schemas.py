# =============================================================================
# VELO Backend — Master Schemas
# =============================================================================
#
# Pydantic schemas for master application flow.
#
# INPUT: MasterApplyRequest — 3-step form collected on frontend, sent as
#   one POST. Fields map to data JSONB sections in MasterProfile.
#
# DOCUMENTS: list[dict] for now (JSONB sandbox). Each dict is freeform —
#   could be {"type": "certificate", "number": "123"} or
#   {"type": "link", "url": "https://..."}.
#   TODO: Replace with file upload when S3/storage is ready.
# =============================================================================

from datetime import datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, StringConstraints

# Constrained string for list items (methods, certifications) to prevent
# oversized payloads. Must be 1–200 characters.
ShortStr = Annotated[str, StringConstraints(min_length=1, max_length=200)]


# ---------------------------------------------------------------------------
# Step 1: Profile info
# ---------------------------------------------------------------------------
class MasterApplyProfile(BaseModel):
    """Step 1 of master application — basic profile."""

    display_name: str = Field(min_length=1, max_length=100)
    email: str | None = Field(default=None, max_length=200)
    phone: str | None = Field(default=None, max_length=30)


# ---------------------------------------------------------------------------
# Step 2: Experience
# ---------------------------------------------------------------------------
class MasterApplyExperience(BaseModel):
    """Step 2 of master application — professional background."""

    methods: list[ShortStr] = Field(min_length=1, max_length=20)
    experience_years: int = Field(ge=0, le=50)
    bio: str | None = Field(default=None, max_length=2000)
    certifications: list[ShortStr] = Field(default_factory=list, max_length=20)


# ---------------------------------------------------------------------------
# Step 3: Documents (JSONB sandbox)
# ---------------------------------------------------------------------------
# Freeform dicts for now. Structure will solidify when file upload is added.
# TODO: Replace with typed schema + file upload (S3) in future phase.


# ---------------------------------------------------------------------------
# Full application request
# ---------------------------------------------------------------------------
class MasterApplyRequest(BaseModel):
    """Combined 3-step master application form."""

    profile: MasterApplyProfile
    experience: MasterApplyExperience
    documents: list[dict] = Field(default_factory=list, max_length=50)


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------
class MasterApplyResponse(BaseModel):
    """Response after submitting master application."""

    user_id: UUID
    status: str
    created_at: datetime


class MasterProfileResponse(BaseModel):
    """Public master profile representation."""

    user_id: UUID
    status: str
    display_name: str | None = None
    bio: str | None = None
    methods: list[str] = Field(default_factory=list)
    experience_years: int | None = None
    frozen_amount: Decimal
    available_amount: Decimal
    created_at: datetime
    updated_at: datetime | None = None
