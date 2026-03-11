# =============================================================================
# VELO Backend -- Admin Master Schemas (Phase 2.3, moved Phase 3.1, NO-LITERALS)
# =============================================================================
#
# NO-LITERALS: note/reason field limits sourced from
#   settings.admin_action_note_max_length -- change once, applies everywhere.
# =============================================================================

from uuid import UUID

from pydantic import BaseModel, Field

from app.core.config import settings


# ---------------------------------------------------------------------------
# Requests
# ---------------------------------------------------------------------------
class VerifyMasterRequest(BaseModel):
    """POST /admin/masters/{user_id}/verify -- request body."""

    notes: str | None = Field(
        default=None,
        max_length=settings.admin_action_note_max_length,
        description="Optional admin notes about verification decision",
    )


class RejectMasterRequest(BaseModel):
    """POST /admin/masters/{user_id}/reject -- request body."""

    reason: str = Field(
        ...,
        min_length=1,
        max_length=settings.admin_action_note_max_length,
        description="Reason for rejection (shown to applicant)",
    )


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------
class AdminMasterActionResponse(BaseModel):
    """Response for verify/reject actions."""

    user_id: UUID
    status: str
