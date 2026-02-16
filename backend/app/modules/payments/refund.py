# =============================================================================
# VELO Backend -- Refund Service (Phase 6.5)
# =============================================================================
#
# Refund and early-finalize logic for booking/practice cancellations.
#
# THREE SCENARIOS:
#
#   A) User cancels > 24h before practice (refund_booking):
#      - Reverse frozen master credit + refund user
#      - Double-entry: master_ledger(-N, frozen) + user_ledger(+N)
#      - Purchase -> REFUNDED
#
#   B) User cancels <= 24h before practice (early_finalize_booking):
#      - Master keeps the money. Immediate unfreeze + commission.
#      - Reversal approach: create offsetting frozen entry, then
#        add available entry and commission -- same net result as
#        finalize_purchases but for a single purchase.
#      - Double-entry:
#          master_ledger(-N, frozen)      -- reverses original frozen credit
#          master_ledger(+N, available)   -- adds to available balance
#          master_ledger(-C, available)   -- commission deduction
#          company_ledger(+C)             -- company revenue
#      - Purchase -> COMPLETED
#
#   C) Master cancels entire practice (refund_all_bookings_for_practice):
#      - 100% refund to every active booking
#      - All waitlist entries -> left
#
# WHY REVERSAL, NOT UPDATE?
#   master_ledger entries don't carry booking_id, so we can't
#   target a specific frozen entry for UPDATE. Instead, we create
#   an offsetting negative frozen entry. When finalize_purchases
#   later runs bulk UPDATE (is_frozen=False), the original and
#   reversal cancel each other out -- cached balances stay correct.
#
# INVARIANTS:
#   - Every refund/early-finalize creates EVEN number of ledger entries
#   - SUM(all ledgers) = 0 after each operation
#   - Free practices (paid_cents=0) get zero-amount entries (proof of path)
#   - Purchase.status guards against double processing (idempotency)
#
# SESSION RULES:
#   No session.commit() (P-01). Caller manages transaction.
# =============================================================================

from datetime import datetime, timezone
from uuid import UUID

import structlog
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import record_audit
from app.core.config import settings
from app.modules.bookings.models import Booking, BookingStatus
from app.modules.payments.models import (
    CompanyLedgerType,
    LedgerStatus,
    MasterLedger,
    Purchase,
    PurchaseStatus,
)
from app.modules.payments.service import (
    record_company_ledger,
    record_master_ledger,
    record_user_ledger,
)
from app.modules.practices.models import Practice
from app.modules.waitlist.models import ACTIVE_STATUSES as WL_ACTIVE, WaitlistStatus, Waitlist

logger = structlog.get_logger()


async def refund_booking(
    *,
    booking: Booking,
    practice: Practice,
    session: AsyncSession,
    cancelled_by_master: bool = False,
) -> Purchase:
    """Refund a single booking: 100% return to user.

    Creates two ledger entries (double-entry reversal):
        master_ledger: -paid_cents (frozen, reverses original credit)
        user_ledger:   +paid_cents (refund to user wallet)

    Even for free practices (paid_cents=0), zero-amount entries
    are created to maintain the double-entry proof-of-path invariant.

    Args:
        booking: The cancelled booking (already status=cancelled).
        practice: The associated practice.
        session: Active async session (caller manages transaction).
        cancelled_by_master: True when master cancelled the practice.

    Returns:
        The updated Purchase (status=REFUNDED).

    Raises:
        None -- silently skips if purchase already processed
        (status != PENDING). This makes the function idempotent.
    """
    # Load purchase with FOR UPDATE (P-12).
    # Use Purchase.booking_id (UNIQUE, always set at creation) instead
    # of booking.purchase_id back-reference which may not be loaded
    # when booking is re-fetched from DB in a separate query.
    stmt = (
        select(Purchase)
        .where(Purchase.booking_id == booking.id)
        .with_for_update()
    )
    result = await session.execute(stmt)
    purchase = result.scalar_one()

    # Idempotency guard: skip if already processed.
    if purchase.status != PurchaseStatus.PENDING.value:
        logger.warning(
            "refund_skipped_not_pending",
            purchase_id=str(purchase.id),
            current_status=purchase.status,
        )
        return purchase

    trigger = "master_cancel" if cancelled_by_master else "user_cancel"
    reason_suffix = f"practice={practice.id}"

    # Double-entry reversal: master debit (frozen) + user credit.
    await record_master_ledger(
        user_id=practice.master_id,
        amount_cents=-purchase.paid_cents,
        reason=f"refund:{reason_suffix}",
        is_frozen=True,
        practice_id=practice.id,
        session=session,
    )
    await record_user_ledger(
        user_id=booking.user_id,
        amount_cents=purchase.paid_cents,
        reason=f"refund:{reason_suffix}",
        session=session,
    )

    # Update purchase status.
    purchase.status = PurchaseStatus.REFUNDED.value

    # Audit.
    await record_audit(
        event="purchase_refunded",
        actor_id=booking.user_id,
        actor_type="system" if cancelled_by_master else "user",
        target_type="purchase",
        target_id=purchase.id,
        data={
            "practice_id": str(practice.id),
            "booking_id": str(booking.id),
            "refunded_cents": purchase.paid_cents,
            "trigger": trigger,
        },
        session=session,
    )

    logger.info(
        "booking_refunded",
        purchase_id=str(purchase.id),
        booking_id=str(booking.id),
        practice_id=str(practice.id),
        user_id=str(booking.user_id),
        refunded_cents=purchase.paid_cents,
        trigger=trigger,
    )

    return purchase


async def early_finalize_booking(
    *,
    booking: Booking,
    practice: Practice,
    session: AsyncSession,
) -> Purchase:
    """Early-finalize a single booking: master keeps the money.

    Used when a user cancels within the deadline window (< 24h).
    The master receives the funds immediately (minus commission),
    rather than waiting for practice finalization.

    Creates ledger entries via reversal approach:
        master_ledger: -paid_cents (frozen, reverses original credit)
        master_ledger: +paid_cents (available, adds to spendable balance)
        master_ledger: -commission  (available, platform fee)
        company_ledger: +commission (platform revenue)

    Even for free practices (paid_cents=0), zero-amount entries
    are created to maintain the double-entry proof-of-path invariant.

    Args:
        booking: The cancelled booking (already status=cancelled).
        practice: The associated practice.
        session: Active async session (caller manages transaction).

    Returns:
        The updated Purchase (status=COMPLETED).

    Raises:
        None -- silently skips if purchase already processed
        (status != PENDING). This makes the function idempotent.
    """
    # Load purchase with FOR UPDATE (P-12).
    # Use Purchase.booking_id (UNIQUE, always set at creation) instead
    # of booking.purchase_id back-reference which may not be loaded
    # when booking is re-fetched from DB in a separate query.
    stmt = (
        select(Purchase)
        .where(Purchase.booking_id == booking.id)
        .with_for_update()
    )
    result = await session.execute(stmt)
    purchase = result.scalar_one()

    # Idempotency guard: skip if already processed.
    if purchase.status != PurchaseStatus.PENDING.value:
        logger.warning(
            "early_finalize_skipped_not_pending",
            purchase_id=str(purchase.id),
            current_status=purchase.status,
        )
        return purchase

    reason_suffix = f"practice={practice.id}"
    # L-07 fix: pure integer math -- no float intermediate.
    commission = purchase.paid_cents * settings.commission_percent // 100

    # Step 1: Reverse the original frozen credit.
    await record_master_ledger(
        user_id=practice.master_id,
        amount_cents=-purchase.paid_cents,
        reason=f"late_cancel_reversal:{reason_suffix}",
        is_frozen=True,
        practice_id=practice.id,
        session=session,
    )

    # Step 2: Add to available balance (unfrozen).
    await record_master_ledger(
        user_id=practice.master_id,
        amount_cents=purchase.paid_cents,
        reason=f"late_cancel_earnings:{reason_suffix}",
        is_frozen=False,
        practice_id=practice.id,
        session=session,
    )

    # Step 3: Deduct commission (double-entry with company).
    await record_master_ledger(
        user_id=practice.master_id,
        amount_cents=-commission,
        reason=f"commission:{reason_suffix}",
        is_frozen=False,
        practice_id=practice.id,
        session=session,
    )
    await record_company_ledger(
        amount_cents=commission,
        ledger_type=CompanyLedgerType.COMMISSION.value,
        reason=f"commission:{reason_suffix}",
        reference_id=purchase.id,
        session=session,
    )

    # Update purchase.
    now = datetime.now(timezone.utc)
    purchase.status = PurchaseStatus.COMPLETED.value
    purchase.commission_cents = commission
    purchase.completed_at = now

    # Audit.
    await record_audit(
        event="purchase_completed",
        actor_id=booking.user_id,
        actor_type="user",
        target_type="purchase",
        target_id=purchase.id,
        data={
            "practice_id": str(practice.id),
            "booking_id": str(booking.id),
            "paid_cents": purchase.paid_cents,
            "commission_cents": commission,
            "trigger": "late_cancel",
        },
        session=session,
    )

    logger.info(
        "booking_early_finalized",
        purchase_id=str(purchase.id),
        booking_id=str(booking.id),
        practice_id=str(practice.id),
        user_id=str(booking.user_id),
        paid_cents=purchase.paid_cents,
        commission_cents=commission,
    )

    return purchase


async def refund_all_bookings_for_practice(
    *,
    practice: Practice,
    session: AsyncSession,
) -> int:
    """Refund all active bookings when master cancels a practice.

    For each confirmed/pending booking:
    1. Set booking status -> cancelled
    2. Call refund_booking (double-entry reversal)

    Also clears the waitlist: all active entries -> left.

    Args:
        practice: The practice being cancelled (already locked FOR UPDATE).
        session: Active async session (caller manages transaction).

    Returns:
        Number of bookings refunded.
    """
    # Load all active bookings with FOR UPDATE (P-12).
    stmt = (
        select(Booking)
        .where(
            Booking.practice_id == practice.id,
            Booking.status.in_({
                BookingStatus.PENDING.value,
                BookingStatus.CONFIRMED.value,
            }),
        )
        .with_for_update()
    )
    result = await session.execute(stmt)
    bookings = list(result.scalars().all())

    now = datetime.now(timezone.utc)
    refunded_count = 0

    for booking in bookings:
        booking.status = BookingStatus.CANCELLED.value
        booking.cancelled_at = now
        booking.cancellation_reason = "Practice cancelled by master"

        await refund_booking(
            booking=booking,
            practice=practice,
            session=session,
            cancelled_by_master=True,
        )
        refunded_count += 1

    # Clear waitlist: all active entries -> left.
    wl_stmt = (
        update(Waitlist)
        .where(
            Waitlist.practice_id == practice.id,
            Waitlist.status.in_(WL_ACTIVE),
        )
        .values(status=WaitlistStatus.LEFT.value)
    )
    wl_result = await session.execute(wl_stmt)
    waitlist_cleared = wl_result.rowcount  # type: ignore[union-attr]

    logger.info(
        "practice_bookings_refunded",
        practice_id=str(practice.id),
        master_id=str(practice.master_id),
        refunded_count=refunded_count,
        waitlist_cleared=waitlist_cleared,
    )

    return refunded_count
