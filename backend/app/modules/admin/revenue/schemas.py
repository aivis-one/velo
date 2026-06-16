# =============================================================================
# VELO Backend -- Admin Revenue Schemas (E9 / 4b)
# =============================================================================
#
# Platform revenue drill-in for the admin dashboard ("Баланс по мастерам").
# All figures are EUR cents, for a calendar period (week|month, UTC):
#   revenue_cents    -- GMV: gross sales (paid_cents) of completed purchases.
#   commission_cents -- platform's cut (CompanyLedger commission).
#   payout_cents     -- net paid out to masters via approved withdrawals
#                       (amount_cents - fee_cents).
#   per_master       -- each master's net earnings + net payouts in the period.
#
# Class names are Admin-prefixed to avoid OpenAPI component-name collisions.
# =============================================================================

from uuid import UUID

from pydantic import BaseModel


class AdminRevenuePerMaster(BaseModel):
    """One master's earnings + payouts within the period."""

    master_id: UUID
    name: str
    earned_cents: int
    payout_cents: int


class AdminRevenueResponse(BaseModel):
    """GET /api/v1/admin/revenue."""

    revenue_cents: int
    commission_cents: int
    payout_cents: int
    per_master: list[AdminRevenuePerMaster]
