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


class RevokeMasterAdvisory(BaseModel):
    """Advisory signals for revoke-preview + revoke (A1, WARN-not-block).

    Mirrors the CLI `set_role.py to_user` downgrade guard, but the admin endpoint
    does NOT block on them (operator decision Б): a revoke soft-freezes the
    profile and preserves every row regardless. Surfaced so the admin sees what
    stays behind before confirming.
    """

    scheduled_or_live_practices: int
    available_cents: int
    frozen_cents: int
    pending_withdrawals: int
    has_warnings: bool


class InviteMasterResponse(BaseModel):
    """POST /admin/masters/invite -- the composed generic invite link.

    Account-agnostic: the link is not bound to a target user. No expiry
    field by design -- the link lives in Redis until the first claim burns
    it (or a Redis flush drops it, after which the admin regenerates).
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
