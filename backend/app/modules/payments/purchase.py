# =============================================================================
# VELO Backend -- Purchase Service (Phase 6.4)
# =============================================================================
#
# Double-entry purchase logic for booking flow.
#
# CREATE PURCHASE (called from create_booking + confirm_waitlist):
#   1. FOR UPDATE on user (balance check, P-07)
#   2. Double-entry: user_ledger(-N) + master_ledger(+N, frozen)
#   3. Create Purchase (paid_cents=N, even if N=0)
#   4. Link booking.purchase_id
#   5. Audit: purchase_created
#
# FINALIZE PURCHASES (called from finalize_practice):
#   1. Unfreeze master_ledger entries (UPDATE is_frozen=False)
#   2. Double-entry commission: master_ledger(-C) + company_ledger(+C)
#   3. Purchase -> completed
#   4. Audit: purchase_completed
#
# INVARIANTS:
#   - Every Booking has exactly one Purchase (Semaphore 1.1/1.2)
#   - Every Purchase creates paired ledger entries (Semaphore 2.1)
#   - Free practices: paid_cents=0, ledger entries with amount=0
#   - Commission entries created even when commission=0 (double-entry)
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
from app.core.exceptions import BadRequestError
from app.modules.bookings.models import Booking
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
from app.modules.users.models import User

logger = structlog.get_logger()


async def create_purchase_for_booking(
    *,
    booking: Booking,
    practice: Practice,
    user: User,
    session: AsyncSession,
) -> Purchase:
    """Create a Purchase linked to a Booking with double-entry ledger.

    Called from create_booking and confirm_waitlist. Always creates
    ledger entries -- even for free practices (amount_cents=0).

    Double-entry pair:
        user_ledger:   -price_cents (debit)
        master_ledger: +price_cents (credit, frozen)

    Args:
        booking: Already-created Booking (flushed, has id).
        practice: Practice being purchased (already loaded with FOR UPDATE).
        user: Buyer (current user).
        session: Active async session (caller manages transaction).

    Returns:
        The created Purchase.

    Raises:
        BadRequestError: If user balance is insufficient for paid practice.
    """
    price_cents = practice.price_cents  # 0 for free practices.

    # FOR UPDATE on user row -- serialize concurrent purchases (P-07).
    user_locked = await session.get(User, user.id, with_for_update=True)
    if user_locked.balance_cents < price_cents:
        raise BadRequestError("Insufficient balance")

    # Double-entry: user debit + master credit (frozen).
    await record_user_ledger(
        user_id=user.id,
        amount_cents=-price_cents,
        reason=f"purchase:practice={practice.id}",
        session=session,
    )
    await record_master_ledger(
        user_id=practice.master_id,
        amount_cents=price_cents,
        reason=f"sale:practice={practice.id}",
        is_frozen=True,
        practice_id=practice.id,
        session=session,
    )

    # Create Purchase record.
    purchase = Purchase(
        user_id=user.id,
        practice_id=practice.id,
        booking_id=booking.id,
        paid_cents=price_cents,
        currency=practice.currency,
        commission_cents=0,
        status=PurchaseStatus.PENDING.value,
    )
    session.add(purchase)
    await session.flush()

    # Link booking -> purchase.
    booking.purchase_id = purchase.id

    # Audit.
    await record_audit(
        event="purchase_created",
        actor_id=user.id,
        actor_type="user",
        target_type="purchase",
        target_id=purchase.id,
        data={
            "practice_id": str(practice.id),
            "booking_id": str(booking.id),
            "paid_cents": price_cents,
            "is_free": practice.is_free,
        },
        session=session,
    )

    logger.info(
        "purchase_created",
        purchase_id=str(purchase.id),
        booking_id=str(booking.id),
        practice_id=str(practice.id),
        user_id=str(user.id),
        paid_cents=price_cents,
    )

    return purchase


async def finalize_purchases(
    *,
    practice_id: UUID,
    practice: Practice,
    session: AsyncSession,
) -> list[Purchase]:
    """Finalize all pending purchases for a completed practice.

    For each pending purchase:
    1. Unfreeze master_ledger entries (UPDATE is_frozen=False)
    2. Calculate commission (paid_cents * commission_percent / 100)
    3. Double-entry: master_ledger(-commission) + company_ledger(+commission)
    4. Mark purchase as completed

    Even for free purchases (paid_cents=0), commission entries are
    created with amount=0 to maintain double-entry invariant.

    Args:
        practice_id: Practice being finalized.
        practice: Practice object (already loaded with FOR UPDATE).
        session: Active async session (caller manages transaction).

    Returns:
        List of finalized Purchase objects.
    """
    commission_rate = settings.commission_percent / 100

    # Get all pending purchases for this practice.
    stmt = (
        select(Purchase)
        .where(
            Purchase.practice_id == practice_id,
            Purchase.status == PurchaseStatus.PENDING.value,
        )
        .with_for_update()
    )
    result = await session.execute(stmt)
    purchases = list(result.scalars().all())

    if not purchases:
        return []

    # Unfreeze all master_ledger entries for this practice (bulk UPDATE).
    unfreeze_stmt = (
        update(MasterLedger)
        .where(
            MasterLedger.practice_id == practice_id,
            MasterLedger.is_frozen.is_(True),
            MasterLedger.status == LedgerStatus.DONE.value,
        )
        .values(is_frozen=False)
    )
    await session.execute(unfreeze_stmt)

    now = datetime.now(timezone.utc)

    for purchase in purchases:
        # Calculate commission (integer math, truncate).
        commission = int(purchase.paid_cents * commission_rate)

        # Double-entry: master debit + company credit.
        await record_master_ledger(
            user_id=practice.master_id,
            amount_cents=-commission,
            reason=f"commission:practice={practice_id}",
            is_frozen=False,
            practice_id=practice_id,
            session=session,
        )
        await record_company_ledger(
            amount_cents=commission,
            ledger_type=CompanyLedgerType.COMMISSION.value,
            reason=f"commission:practice={practice_id}",
            reference_id=purchase.id,
            session=session,
        )

        # Update purchase.
        purchase.status = PurchaseStatus.COMPLETED.value
        purchase.commission_cents = commission
        purchase.completed_at = now

        # Audit.
        await record_audit(
            event="purchase_completed",
            actor_id=None,
            actor_type="system",
            target_type="purchase",
            target_id=purchase.id,
            data={
                "practice_id": str(practice_id),
                "user_id": str(purchase.user_id),
                "paid_cents": purchase.paid_cents,
                "commission_cents": commission,
            },
            session=session,
        )

    logger.info(
        "purchases_finalized",
        practice_id=str(practice_id),
        count=len(purchases),
        total_commission=sum(p.commission_cents for p in purchases),
    )

    return purchases
