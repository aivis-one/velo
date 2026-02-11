# =============================================================================
# VELO Backend -- Report Schemas (Phase 3.3)
# =============================================================================
#
# Pydantic schemas for user-facing report endpoints.
#
# CREATE: user submits a report (target_type, target_id, reason).
# UPDATE: user edits their own pending report (reason only).
# RESPONSE: report data returned to user/admin.
# =============================================================================

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# User-facing: create / update / response
# ---------------------------------------------------------------------------


class CreateReportRequest(BaseModel):
    """User submits a new report."""

    target_type: Literal["user", "master", "practice"]
    target_id: UUID
    reason: str = Field(min_length=1, max_length=2000)


class UpdateReportRequest(BaseModel):
    """User edits their own pending report (reason only)."""

    reason: str = Field(min_length=1, max_length=2000)


class ReportResponse(BaseModel):
    """Single report -- returned to both user and admin."""

    id: UUID
    reporter_id: UUID
    target_type: str
    target_id: UUID
    reason: str
    status: str
    resolved_by: UUID | None = None
    resolution_note: str | None = None
    resolved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime | None = None


class ExistingReportResponse(BaseModel):
    """Returned when user tries to create a duplicate report.

    Contains the existing report + a message suggesting to edit it.
    """

    message: str = "You already reported this target. You can edit your report."
    report: ReportResponse
