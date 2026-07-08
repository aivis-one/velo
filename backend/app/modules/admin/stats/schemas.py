# =============================================================================
# VELO Backend -- Admin Stats Schemas (Phase 3.1, updated Phase 4.1)
# =============================================================================

from pydantic import BaseModel, Field


class AdminStatsResponse(BaseModel):
    """GET /api/v1/admin/stats -- response body."""

    users_count: int = Field(description="Total registered users")
    masters_count: int = Field(description="Users with role=master")
    practices_count: int = Field(description="Total practices")
    pending_verifications: int = Field(
        description="Master applications awaiting admin review",
    )
    pending_method_changes: int = Field(
        description="Master method-change requests awaiting admin review",
    )
