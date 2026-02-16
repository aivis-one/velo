# =============================================================================
# VELO Backend -- Stripe Integration (Phase 6.3)
# =============================================================================
#
# Thin wrapper around Stripe SDK for:
#   1. Creating Checkout Sessions (topup flow)
#   2. Verifying webhook signatures
#   3. Handling completed/failed checkout events
#
# IDEMPOTENCY:
#   Webhook handlers check Payment.status before acting.
#   Duplicate webhooks for already-confirmed payments are no-ops.
#
# SESSION RULES:
#   No session.commit() here (P-01). Caller handles transaction.
#
# TESTING:
#   Unit tests mock stripe module entirely (no real API calls).
#   Integration tests use Stripe Test Mode (separate test file).
# =============================================================================

import asyncio
from datetime import UTC, datetime
from uuid import UUID

import stripe
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import record_audit
from app.core.config import settings
from app.core.exceptions import BadRequestError
from app.modules.payments.models import (
    Payment,
    PaymentDirection,
    PaymentStatus,
)
from app.modules.payments.service import record_user_ledger

logger = structlog.get_logger()


def _configure_stripe() -> None:
    """Set Stripe API key from settings.

    Called lazily -- not at import time, so tests can mock settings.
    """
    stripe.api_key = settings.stripe_secret_key


# ---------------------------------------------------------------------------
# Create Checkout Session
# ---------------------------------------------------------------------------


async def create_topup_session(
    *,
    user_id: UUID,
    amount_cents: int,
    currency: str,
    session: AsyncSession,
) -> tuple[Payment, str]:
    """Create a Stripe Checkout Session for balance topup.

    1. Create a Payment record (status=pending).
    2. Call Stripe API to create a Checkout Session.
    3. Store stripe_session_id on the Payment.
    4. Record audit event.

    Args:
        user_id: The user topping up.
        amount_cents: Amount in cents.
        currency: Currency code (e.g. "eur").
        session: Active DB session (caller manages transaction).

    Returns:
        Tuple of (Payment, checkout_url).

    Raises:
        BadRequestError: If Stripe API call fails.
    """
    _configure_stripe()

    # Guard: reject topup if Stripe is not configured (stub mode).
    if settings.is_stripe_stub:
        raise BadRequestError(
            "Payment system is not configured yet"
        )

    # Step 1: Create pending Payment record.
    payment = Payment(
        user_id=user_id,
        direction=PaymentDirection.IN.value,
        amount_cents=amount_cents,
        currency=currency,
        status=PaymentStatus.PENDING.value,
    )
    session.add(payment)
    await session.flush()

    # Step 2: Create Stripe Checkout Session.
    # H-01 fix: stripe SDK is synchronous -- offload to thread pool
    # to avoid blocking the asyncio event loop (200ms-2s per call).
    try:
        checkout = await asyncio.to_thread(
            stripe.checkout.Session.create,
            mode="payment",
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": currency,
                        "unit_amount": amount_cents,
                        "product_data": {
                            "name": "VELO Balance Top-up",
                            "description": (
                                f"Top up {amount_cents / 100:.2f} "
                                f"{currency.upper()}"
                            ),
                        },
                    },
                    "quantity": 1,
                },
            ],
            metadata={
                "payment_id": str(payment.id),
                "user_id": str(user_id),
            },
            success_url=settings.stripe_success_url,
            cancel_url=settings.stripe_cancel_url,
        )
    except stripe.StripeError as exc:
        logger.error(
            "stripe_checkout_creation_failed",
            user_id=str(user_id),
            amount_cents=amount_cents,
            error=str(exc),
        )
        raise BadRequestError(
            "Failed to create payment session"
        ) from None

    # Step 3: Store Stripe session ID.
    payment.stripe_session_id = checkout.id
    await session.flush()

    # Step 4: Audit.
    await record_audit(
        event="payment_topup_created",
        actor_id=user_id,
        actor_type="user",
        target_type="payment",
        target_id=payment.id,
        data={
            "amount_cents": amount_cents,
            "currency": currency,
            "stripe_session_id": checkout.id,
        },
        session=session,
    )

    logger.info(
        "topup_session_created",
        payment_id=str(payment.id),
        user_id=str(user_id),
        amount_cents=amount_cents,
        stripe_session_id=checkout.id,
    )

    return payment, checkout.url


# ---------------------------------------------------------------------------
# Webhook Verification
# ---------------------------------------------------------------------------


def verify_webhook_signature(
    payload: bytes,
    sig_header: str,
) -> dict:
    """Verify Stripe webhook signature and return parsed event.

    Args:
        payload: Raw request body bytes.
        sig_header: Value of Stripe-Signature header.

    Returns:
        Parsed Stripe event dict.

    Raises:
        BadRequestError: If signature verification fails.
    """
    _configure_stripe()

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.stripe_webhook_secret,
        )
    except ValueError:
        logger.warning("stripe_webhook_invalid_payload")
        raise BadRequestError("Invalid payload") from None
    except stripe.SignatureVerificationError:
        logger.warning(
            "stripe_webhook_signature_failed",
            sig_header=sig_header[:20] + "...",
        )
        raise BadRequestError("Invalid signature") from None

    return event


# ---------------------------------------------------------------------------
# Event Handlers
# ---------------------------------------------------------------------------


async def handle_checkout_completed(
    event_data: dict,
    session: AsyncSession,
) -> Payment | None:
    """Handle checkout.session.completed webhook event.

    1. Look up Payment by stripe_session_id.
    2. Skip if already confirmed (idempotency).
    3. Update Payment status -> confirmed.
    4. Record user_ledger entry (balance topup).
    5. Record audit event.

    Args:
        event_data: The Stripe event data object (checkout session).
        session: Active DB session.

    Returns:
        Updated Payment, or None if skipped (idempotent).
    """
    stripe_session_id = event_data.get("id")
    if not stripe_session_id:
        logger.warning("stripe_webhook_missing_session_id")
        return None

    # Look up payment by stripe_session_id.
    stmt = (
        select(Payment)
        .where(Payment.stripe_session_id == stripe_session_id)
        .with_for_update()
    )
    result = await session.execute(stmt)
    payment = result.scalar_one_or_none()

    if not payment:
        logger.warning(
            "stripe_webhook_payment_not_found",
            stripe_session_id=stripe_session_id,
        )
        return None

    # Idempotency: skip if already confirmed.
    if payment.status == PaymentStatus.CONFIRMED.value:
        logger.info(
            "stripe_webhook_already_confirmed",
            payment_id=str(payment.id),
            stripe_session_id=stripe_session_id,
        )
        return payment

    # Update payment.
    now = datetime.now(UTC)
    payment.status = PaymentStatus.CONFIRMED.value
    payment.confirmed_at = now
    payment.stripe_payment_intent_id = event_data.get(
        "payment_intent"
    )
    payment.stripe_metadata = {
        "stripe_event": {
            "customer_email": event_data.get("customer_email"),
            "amount_total": event_data.get("amount_total"),
            "currency": event_data.get("currency"),
        },
    }

    # Record user_ledger entry (actual balance topup).
    await record_user_ledger(
        user_id=payment.user_id,
        amount_cents=payment.amount_cents,
        reason=f"payment:{payment.id}",
        session=session,
        notes=f"Stripe topup, session={stripe_session_id}",
    )

    # Audit.
    await record_audit(
        event="payment_topup_confirmed",
        actor_id=None,
        actor_type="system",
        target_type="payment",
        target_id=payment.id,
        data={
            "amount_cents": payment.amount_cents,
            "currency": payment.currency,
            "stripe_session_id": stripe_session_id,
            "stripe_payment_intent_id": payment.stripe_payment_intent_id,
        },
        session=session,
    )

    logger.info(
        "topup_confirmed",
        payment_id=str(payment.id),
        user_id=str(payment.user_id),
        amount_cents=payment.amount_cents,
    )

    return payment


async def handle_checkout_expired_or_failed(
    event_data: dict,
    session: AsyncSession,
) -> Payment | None:
    """Handle checkout.session.expired or payment failure events.

    1. Look up Payment by stripe_session_id.
    2. Skip if already in terminal state (idempotency).
    3. Update Payment status -> failed.
    4. Record audit event.

    Args:
        event_data: The Stripe event data object.
        session: Active DB session.

    Returns:
        Updated Payment, or None if skipped.
    """
    stripe_session_id = event_data.get("id")
    if not stripe_session_id:
        logger.warning("stripe_webhook_missing_session_id")
        return None

    stmt = (
        select(Payment)
        .where(Payment.stripe_session_id == stripe_session_id)
        .with_for_update()
    )
    result = await session.execute(stmt)
    payment = result.scalar_one_or_none()

    if not payment:
        logger.warning(
            "stripe_webhook_payment_not_found",
            stripe_session_id=stripe_session_id,
        )
        return None

    # Idempotency: skip if already in terminal state.
    terminal = {
        PaymentStatus.CONFIRMED.value,
        PaymentStatus.FAILED.value,
        PaymentStatus.REFUNDED.value,
    }
    if payment.status in terminal:
        logger.info(
            "stripe_webhook_already_terminal",
            payment_id=str(payment.id),
            status=payment.status,
        )
        return payment

    payment.status = PaymentStatus.FAILED.value

    # Audit.
    await record_audit(
        event="payment_topup_failed",
        actor_id=None,
        actor_type="system",
        target_type="payment",
        target_id=payment.id,
        data={
            "amount_cents": payment.amount_cents,
            "currency": payment.currency,
            "stripe_session_id": stripe_session_id,
            "reason": "checkout_expired_or_failed",
        },
        session=session,
    )

    logger.info(
        "topup_failed",
        payment_id=str(payment.id),
        user_id=str(payment.user_id),
    )

    return payment
