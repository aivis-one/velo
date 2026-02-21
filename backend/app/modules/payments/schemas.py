# =============================================================================
# VELO Backend -- Payment Schemas (Phase 6.3, updated Phase 6.7)
# =============================================================================
#
# Pydantic schemas for payment (topup) and purchase endpoints.
#
# TopupRequest:                   amount_cents from user.
# TopupResponse:                  Stripe checkout URL + payment ID.
# PaymentResponse:                full payment record representation.
# PurchaseResponse:               purchase details with financial info.
# PurchaseWithPracticeResponse:   purchase + PracticeSummary (for list views).
# PaginatedPurchasesResponse:     paginated list of purchases.
# =============================================================================

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.config import settings
from app.modules.practices.schemas import PracticeSummary


class TopupRequest(BaseModel):
    """POST /api/v1/payments/topup -- request body."""

    amount_cents: int = Field(
        ge=settings.min_topup_cents,
        le=settings.max_topup_cents,
        description="Amount to top up in EUR cents.",
    )


class TopupResponse(BaseModel):
    """POST /api/v1/payments/topup -- response body."""

    payment_id: UUID
    checkout_url: str
    amount_cents: int
    currency: str


class PaymentResponse(BaseModel):
    """Full payment record representation."""

    id: UUID
    user_id: UUID
    direction: str
    amount_cents: int
    currency: str
    status: str
    stripe_session_id: str | None
    stripe_payment_intent_id: str | None
    created_at: datetime
    confirmed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


# -- Purchase (Phase 6.4, updated Phase 6.7) --------------------------------


class PurchaseResponse(BaseModel):
    """Purchase details returned to client.

    Phase 6.7: added amount_cents, discount_cents, promo_id.
    Invariant: paid_cents = amount_cents - discount_cents.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    practice_id: UUID
    booking_id: UUID
    promo_id: UUID | None
    amount_cents: int
    discount_cents: int
    paid_cents: int
    currency: str
    commission_cents: int
    status: str
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime | None


# -- Frontend Backlog: Enriched purchase schemas ---------------------------


class PurchaseWithPracticeResponse(BaseModel):
    """Purchase with lightweight practice summary for list views.

    Used by GET /api/v1/purchases/me. Gives the frontend enough data
    for purchase history rendering (title, time, amount, status).
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    practice_id: UUID
    booking_id: UUID
    promo_id: UUID | None
    amount_cents: int
    discount_cents: int
    paid_cents: int
    currency: str
    commission_cents: int
    status: str
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime | None
    practice: PracticeSummary


class PaginatedPurchasesResponse(BaseModel):
    """GET /api/v1/purchases/me -- paginated list."""

    items: list[PurchaseWithPracticeResponse]
    total: int
    limit: int
    offset: int
