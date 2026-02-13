# =============================================================================
# VELO Backend -- Payment Schemas (Phase 6.3)
# =============================================================================
#
# Pydantic schemas for payment (topup) endpoints.
#
# TopupRequest:  amount_cents from user, validated against config limits.
# TopupResponse: returns Stripe checkout URL + payment ID.
# PaymentResponse: full payment record representation.
# =============================================================================

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.core.config import settings


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

    model_config = {"from_attributes": True}
