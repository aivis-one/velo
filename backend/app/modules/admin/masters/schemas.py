# =============================================================================
# VELO Backend -- Admin Master Schemas (Phase 2.3, moved Phase 3.1)
# =============================================================================

from uuid import UUID

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Requests
# ---------------------------------------------------------------------------
class VerifyMasterRequest(BaseModel):
    """POST /admin/masters/{user_id}/verify -- request body."""

    notes: str | None = Field(
        default=None,
        max_length=1000,
        description="Optional admin notes about verification decision",
    )


class RejectMasterRequest(BaseModel):
    """POST /admin/masters/{user_id}/reject -- request body."""

    reason: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Reason for rejection (shown to applicant)",
    )


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------
class AdminMasterActionResponse(BaseModel):
    """Response for verify/reject actions."""

    user_id: UUID
    status: str
