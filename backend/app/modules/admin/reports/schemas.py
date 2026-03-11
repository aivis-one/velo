# =============================================================================
# VELO Backend -- Admin Report Schemas (Phase 3.3, NO-LITERALS)
# =============================================================================
#
# NO-LITERALS: resolution note field limits sourced from
#   settings.admin_report_note_max_length -- change once, applies everywhere.
# =============================================================================

from pydantic import BaseModel, Field

from app.core.config import settings
from app.modules.reports.schemas import ReportResponse


# ---------------------------------------------------------------------------
# Admin actions
# ---------------------------------------------------------------------------


class ResolveReportRequest(BaseModel):
    """Admin resolves a report."""

    resolution_note: str = Field(
        min_length=1, max_length=settings.admin_report_note_max_length,
    )


class DismissReportRequest(BaseModel):
    """Admin dismisses a report."""

    resolution_note: str | None = Field(
        default=None, max_length=settings.admin_report_note_max_length,
    )


# ---------------------------------------------------------------------------
# Admin listing
# ---------------------------------------------------------------------------


class PaginatedReportsResponse(BaseModel):
    """GET /api/v1/admin/reports -- paginated report list."""

    items: list[ReportResponse]
    total: int
    limit: int
    offset: int
