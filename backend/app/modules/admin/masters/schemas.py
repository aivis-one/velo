# =============================================================================
# VELO Backend -- Admin Master Schemas (Phase 2.3, moved Phase 3.1, NO-LITERALS)
# =============================================================================
#
# NO-LITERALS: note/reason field limits sourced from
#   settings.admin_action_note_max_length -- change once, applies everywhere.
# =============================================================================

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.core.config import settings


# ---------------------------------------------------------------------------
# Requests
# ---------------------------------------------------------------------------
class InviteMasterRequest(BaseModel):
    """POST /admin/masters/invite -- request body (Batch-INVITE, C1=Б).

    telegram_id identifies the invitee; the person must have opened the bot
    at least once (a User row must exist), else 404 invite_target_not_found.
    """

    telegram_id: int
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


class InviteMasterResponse(BaseModel):
    """POST /admin/masters/invite -- the composed one-time invite link.

    No expiry field by design (TTL=В): the link is one-time and lives until
    claimed; re-issuing overwrites (kills) the previous link.
    """

    invite_link: str
    issued_at: datetime
