# =============================================================================
# VELO Backend -- Promo Schemas (Phase 6.7)
# =============================================================================
#
# CreateMasterPromoRequest: master creates a promo code.
# PromoResponse:            full promo record.
# PaginatedPromosResponse:  paginated list for master/admin views.
# =============================================================================

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CreateMasterPromoRequest(BaseModel):
    """POST /api/v1/masters/me/promos -- create a master promo code.

    Master promos: master absorbs the discount from their revenue.
    type and master_id are set automatically by the service layer.
    """

    code: str = Field(
        min_length=3, max_length=50,
        description="Unique promo code (will be uppercased).",
    )
    discount_percent: int = Field(
        gt=0, le=100,
        description="Discount percentage (must be in allowed list).",
    )
    practice_id: UUID | None = Field(
        default=None,
        description="Limit promo to a specific practice (null = all).",
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


class PromoResponse(BaseModel):
    """Full promo record returned to master and admin."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    type: str
    master_id: UUID | None
    practice_id: UUID | None
    discount_percent: int
    max_uses: int | None
    used_count: int
    valid_from: datetime
    valid_until: datetime | None
    first_purchase_only: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime | None


class PaginatedPromosResponse(BaseModel):
    """Paginated list of promos."""

    items: list[PromoResponse]
    total: int
    limit: int
    offset: int
