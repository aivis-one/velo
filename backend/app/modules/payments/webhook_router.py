# =============================================================================
# VELO Backend -- Stripe Webhook Router (Phase 6.3)
# =============================================================================
#
# ENDPOINT:
#   POST /webhooks/stripe -- receives Stripe webhook events
#
# NO AUTH: Stripe authenticates via webhook signature (Stripe-Signature
#   header). No Bearer token or session required.
#
# RAW BODY: Stripe signature verification requires the raw request body
#   (bytes), not parsed JSON. We use Request.body() before any parsing.
#
# SESSION MANAGEMENT:
#   Webhook cannot use Depends(get_db_session) because there is no auth
#   dependency chain. We create a session manually via get_session_factory()
#   and manage commit/rollback explicitly.
#
# IDEMPOTENCY: Handlers skip already-processed events (safe to retry).
#
# HANDLED EVENTS:
#   checkout.session.completed -- topup confirmed
#   checkout.session.expired   -- topup failed (session timed out)
# =============================================================================

import structlog
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.core.database import get_session_factory
from app.modules.payments.stripe import (
    handle_checkout_completed,
    handle_checkout_expired_or_failed,
    verify_webhook_signature,
)

logger = structlog.get_logger()

webhook_router = APIRouter(
    prefix="/webhooks", tags=["webhooks"],
)

# Events we handle. Others are logged and ignored.
_HANDLED_EVENTS = {
    "checkout.session.completed",
    "checkout.session.expired",
}


@webhook_router.post("/stripe")
async def stripe_webhook(request: Request) -> JSONResponse:
    """Receive and process Stripe webhook events.

    1. Read raw body (required for signature verification).
    2. Verify signature using Stripe-Signature header.
    3. Dispatch to event-specific handler.
    4. Return 200 to acknowledge receipt.

    Always returns 200 to Stripe after successful signature check --
    even for unhandled events or processing errors. Stripe retries
    on non-2xx, and we don't want retries for events we
    intentionally skip.
    """
    # Step 1: Raw body.
    payload = await request.body()

    # Step 2: Signature verification.
    sig_header = request.headers.get("stripe-signature", "")
    if not sig_header:
        logger.warning("stripe_webhook_missing_signature")
        return JSONResponse(
            status_code=400,
            content={"error": "Missing Stripe-Signature header"},
        )

    try:
        event = verify_webhook_signature(payload, sig_header)
    except Exception:
        # verify_webhook_signature raises BadRequestError
        # on invalid signature / payload. Return 400.
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid signature"},
        )

    event_type = event.get("type", "unknown")
    event_id = event.get("id", "unknown")

    logger.info(
        "stripe_webhook_received",
        event_type=event_type,
        event_id=event_id,
    )

    # Step 3: Skip unhandled events.
    if event_type not in _HANDLED_EVENTS:
        logger.info(
            "stripe_webhook_unhandled_event",
            event_type=event_type,
        )
        return JSONResponse(
            status_code=200,
            content={"status": "ignored"},
        )

    # Step 4: Process with manual session management.
    factory = get_session_factory()
    session = factory()
    try:
        event_data = event.get("data", {}).get("object", {})

        if event_type == "checkout.session.completed":
            await handle_checkout_completed(event_data, session)
        elif event_type == "checkout.session.expired":
            await handle_checkout_expired_or_failed(
                event_data, session,
            )

        await session.commit()

        logger.info(
            "stripe_webhook_processed",
            event_type=event_type,
            event_id=event_id,
        )
    except Exception:
        await session.rollback()
        logger.exception(
            "stripe_webhook_processing_error",
            event_type=event_type,
            event_id=event_id,
        )
        # Return 200 even on error -- we don't want Stripe to
        # retry if our business logic failed. Payment stays
        # in pending state for manual investigation.
    finally:
        await session.close()

    return JSONResponse(
        status_code=200,
        content={"status": "processed"},
    )
