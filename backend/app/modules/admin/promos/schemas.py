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
#
# CR-01: valid_from changed from required to optional (same as
#   CreateMasterPromoRequest). Defaults to utcnow() via validator.
# =============================================================================

from datetime import datetime, timezone

from pydantic import BaseModel, Field, field_validator


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
    valid_from: datetime | None = Field(
        default=None,
        validate_default=True,
        description=(
            "Start of validity window (UTC). "
            "Defaults to current time when omitted."
        ),
    )
    valid_until: datetime | None = Field(
        default=None,
        description="End of validity window (null = no expiry).",
    )
    first_purchase_only: bool = Field(
        default=False,
        description="If true, only works for user's first purchase.",
    )

    @field_validator("valid_from", mode="before")
    @classmethod
    def default_valid_from_to_now(cls, v: datetime | None) -> datetime:
        """Default valid_from to current UTC time when not provided.

        Guarantees downstream code always receives a concrete datetime,
        so service-layer comparisons (valid_until <= valid_from) work
        without None checks.
        """
        if v is None:
            return datetime.now(timezone.utc)
        return v
