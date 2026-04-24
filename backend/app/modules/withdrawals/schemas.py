# =============================================================================
# VELO Backend -- Withdrawal Schemas (Phase 6.6)
# =============================================================================
#
# Pydantic schemas for master withdrawal endpoints.
#
# CreateWithdrawalRequest: amount_cents from master.
# WithdrawalResponse:      full withdrawal record.
# PaginatedWithdrawalsResponse: paginated list (master + admin views).
#
# CR-01: WithdrawalResponse.status uses WithdrawalStatus StrEnum instead
#   of str so OpenAPI emits enum values and generated TypeScript types
#   produce union literals instead of plain string.
# =============================================================================

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.masters.schemas import PayoutDetails
from app.modules.withdrawals.models import WithdrawalStatus


class CreateWithdrawalRequest(BaseModel):
    """POST /api/v1/masters/me/withdraw -- request body.

    amount_cents is the total withdrawal amount (fee deducted from it).
    Minimum enforced in service against settings.min_withdrawal_cents.
    """

    amount_cents: int = Field(ge=1)


class WithdrawalResponse(BaseModel):
    """Full withdrawal record returned to master and admin."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    amount_cents: int
    fee_cents: int
    currency: str
    status: WithdrawalStatus
    payout_details: PayoutDetails
    admin_id: UUID | None
    admin_note: str | None
    approved_at: datetime | None
    rejected_at: datetime | None
    created_at: datetime
    updated_at: datetime | None


class PaginatedWithdrawalsResponse(BaseModel):
    """Paginated list of withdrawals."""

    items: list[WithdrawalResponse]
    total: int
    limit: int
    offset: int
