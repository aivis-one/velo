# =============================================================================
# VELO Backend -- Admin Report Schemas (Phase 3.3)
# =============================================================================
#
# Schemas for admin report management endpoints.
# =============================================================================

from pydantic import BaseModel, Field

from app.modules.reports.schemas import ReportResponse


# ---------------------------------------------------------------------------
# Admin actions
# ---------------------------------------------------------------------------


class ResolveReportRequest(BaseModel):
    """Admin resolves a report."""

    resolution_note: str = Field(min_length=1, max_length=2000)


class DismissReportRequest(BaseModel):
    """Admin dismisses a report."""

    resolution_note: str | None = Field(default=None, max_length=2000)


# ---------------------------------------------------------------------------
# Admin listing
# ---------------------------------------------------------------------------


class PaginatedReportsResponse(BaseModel):
    """GET /api/v1/admin/reports -- paginated report list."""

    items: list[ReportResponse]
    total: int
    limit: int
    offset: int
