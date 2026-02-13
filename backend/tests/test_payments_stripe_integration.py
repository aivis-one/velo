# =============================================================================
# Tests: Stripe Integration (Phase 6.3) — REAL Stripe Test Mode
# =============================================================================
#
# These tests hit the real Stripe API in test mode.
# Skipped by default — run only with:
#   STRIPE_TEST_MODE=1 pytest tests/test_payments_stripe_integration.py -v
#
# Requirements:
#   - STRIPE_SECRET_KEY must be a real sk_test_... key
#   - STRIPE_WEBHOOK_SECRET can be any value (webhooks not tested here)
#
# telegram_id range: 74xxx (stripe integration tests)
# =============================================================================

import os

import pytest
import stripe
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.payments.models import (
    Payment,
    PaymentDirection,
    PaymentStatus,
)
from app.modules.payments.stripe import create_topup_session
from app.modules.users.models import User, UserRole

# Skip all tests in this module unless STRIPE_TEST_MODE=1.
pytestmark = pytest.mark.skipif(
    os.environ.get("STRIPE_TEST_MODE") != "1",
    reason="Stripe integration tests require STRIPE_TEST_MODE=1",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _create_user(
    session: AsyncSession, telegram_id: int,
) -> User:
    """Create a bare User row for integration tests."""
    user = User(
        telegram_id=telegram_id,
        first_name="StripeIntTest",
        role=UserRole.USER,
    )
    session.add(user)
    await session.flush()
    return user


# ---------------------------------------------------------------------------
# Integration tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_real_stripe_checkout_session_creation(
    db_session: AsyncSession,
) -> None:
    """Create a real Stripe Checkout Session in test mode.

    Verifies:
    - Stripe API accepts our request format.
    - Session URL is returned (starts with https://checkout.stripe.com).
    - Payment record is created with correct stripe_session_id.
    """
    user = await _create_user(db_session, telegram_id=74001)

    payment, checkout_url = await create_topup_session(
        user_id=user.id,
        amount_cents=1000,
        currency="eur",
        session=db_session,
    )

    # Payment created correctly.
    assert payment.user_id == user.id
    assert payment.amount_cents == 1000
    assert payment.status == PaymentStatus.PENDING.value
    assert payment.direction == PaymentDirection.IN.value

    # Stripe session ID looks real.
    assert payment.stripe_session_id is not None
    assert payment.stripe_session_id.startswith("cs_test_")

    # Checkout URL points to Stripe.
    assert checkout_url.startswith("https://checkout.stripe.com")


@pytest.mark.asyncio
async def test_real_stripe_session_retrievable(
    db_session: AsyncSession,
) -> None:
    """Created session can be retrieved from Stripe API."""
    user = await _create_user(db_session, telegram_id=74002)

    payment, _ = await create_topup_session(
        user_id=user.id,
        amount_cents=500,
        currency="eur",
        session=db_session,
    )

    # Retrieve the session directly from Stripe.
    stripe.api_key = settings.stripe_secret_key
    retrieved = stripe.checkout.Session.retrieve(
        payment.stripe_session_id,
    )

    assert retrieved.id == payment.stripe_session_id
    assert retrieved.amount_total == 500
    assert retrieved.currency == "eur"
    assert retrieved.status == "open"
    assert retrieved.metadata.get("payment_id") == str(payment.id)
    assert retrieved.metadata.get("user_id") == str(user.id)


@pytest.mark.asyncio
async def test_real_stripe_minimum_amount(
    db_session: AsyncSession,
) -> None:
    """Stripe accepts minimum topup amount (EUR 1.00 = 100 cents)."""
    user = await _create_user(db_session, telegram_id=74003)

    payment, checkout_url = await create_topup_session(
        user_id=user.id,
        amount_cents=100,
        currency="eur",
        session=db_session,
    )

    assert payment.amount_cents == 100
    assert checkout_url.startswith("https://checkout.stripe.com")
