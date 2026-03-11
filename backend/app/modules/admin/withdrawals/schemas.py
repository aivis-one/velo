# =============================================================================
# VELO Backend -- Admin Withdrawals Schemas (Phase 6.6, Batch 3, NO-LITERALS)
# =============================================================================
#
# NO-LITERALS: note field limits sourced from
#   settings.admin_action_note_max_length -- change once, applies everywhere.
# =============================================================================

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.core.config import settings


class ApproveWithdrawalRequest(BaseModel):
    """POST /admin/withdrawals/{id}/approve -- optional admin note."""

    note: str | None = Field(
        default=None, max_length=settings.admin_action_note_max_length,
    )


class RejectWithdrawalRequest(BaseModel):
    """POST /admin/withdrawals/{id}/reject -- reason required."""

    note: str = Field(
        min_length=1, max_length=settings.admin_action_note_max_length,
    )


class AdminWithdrawalResponse(BaseModel):
    """Single withdrawal record for admin view."""

    id: UUID
    user_id: UUID
    amount_cents: int
    fee_cents: int
    currency: str
    status: str
    payout_details: dict
    admin_id: UUID | None = None
    admin_note: str | None = None
    approved_at: datetime | None = None
    rejected_at: datetime | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class PaginatedAdminWithdrawalsResponse(BaseModel):
    """Paginated list of withdrawals for admin."""

    items: list[AdminWithdrawalResponse]
    total: int
    limit: int
    offset: int
