# =============================================================================
# VELO Backend -- Admin Promo Schemas (Phase 6.7, Batch 3)
# =============================================================================
#
# CreateCompanyPromoRequest: admin creates a platform-wide promo code.
#   Company promos are always global (practice_id=None, master_id=None).
#   The company pays for the discount from the marketing budget.
#
# Response schemas are reused from promos/schemas.py:
#   PromoResponse, PaginatedPromosResponse.
# =============================================================================

from datetime import datetime

from pydantic import BaseModel, Field


class CreateCompanyPromoRequest(BaseModel):
    """POST /api/v1/admin/promos -- create a company promo code.

    Company promos: company pays for the discount from marketing budget.
    type=company and master_id=None are set automatically by the service.
    practice_id is always None (company promos are platform-wide).
    """

    code: str = Field(
        min_length=3, max_length=50,
        description="Unique promo code (will be uppercased).",
    )
    discount_percent: int = Field(
        gt=0, le=100,
        description="Discount percentage (must be in allowed list).",
    )
    max_uses: int | None = Field(
        default=None, ge=1,
        description="Max number of uses (null = unlimited).",
    )
    valid_from: datetime = Field(
        description="Start of validity window (UTC).",
    )
    valid_until: datetime | None = Field(
        default=None,
        description="End of validity window (null = no expiry).",
    )
    first_purchase_only: bool = Field(
        default=False,
        description="If true, only works for user's first purchase.",
    )
