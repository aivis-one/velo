# =============================================================================
# VELO Backend -- Admin Master Schemas (Phase 2.3, moved Phase 3.1, NO-LITERALS)
# =============================================================================
#
# NO-LITERALS: note/reason field limits sourced from
#   settings.admin_action_note_max_length -- change once, applies everywhere.
# =============================================================================

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, StringConstraints

from app.core.config import settings

# Constrained method string, mirroring masters/schemas.ShortStr (defined here
# to avoid a cross-module import). Non-empty, capped at 200 chars.
_MethodStr = Annotated[str, StringConstraints(min_length=1, max_length=200)]


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


class EditMasterMethodsRequest(BaseModel):
    """PATCH /admin/masters/{user_id}/methods -- new flat method set (T3).

    Admin-authored direct edit of a master's methods during review. Mirrors the
    apply-side rule (min 1, max 20). Distinct from the master's own
    method-change request (M3).
    """

    methods: list[_MethodStr] = Field(min_length=1, max_length=20)


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


# ---------------------------------------------------------------------------
# M3 (E19-FLAT): method change-request moderation
# ---------------------------------------------------------------------------
class AdminMethodChangeItem(BaseModel):
    """One pending method change-request in the admin moderation list.

    Carries the master's identity + the current vs proposed flat method sets
    so the admin can decide without a second fetch.
    """

    user_id: UUID
    display_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    avatar_url: str | None = None
    current_methods: list[str] = Field(default_factory=list)
    proposed_methods: list[str] = Field(default_factory=list)
    submitted_at: datetime


class PaginatedMethodChangeRequestsResponse(BaseModel):
    """GET /admin/masters/method-change-requests -- paginated pending list."""

    items: list[AdminMethodChangeItem]
    total: int
    limit: int
    offset: int


class RejectMethodChangeRequest(BaseModel):
    """POST /admin/masters/{user_id}/method-change-request/reject -- body."""

    reason: str = Field(
        ...,
        min_length=1,
        max_length=settings.admin_action_note_max_length,
        description="Reason for rejecting the method change (shown to master)",
    )


class MethodChangeActionResponse(BaseModel):
    """Response for approve/reject method-change actions.

    status is the resulting request state: "approved" (methods updated,
    request cleared) or "rejected".
    """

    user_id: UUID
    status: str
