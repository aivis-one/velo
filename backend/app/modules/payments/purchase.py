# =============================================================================
# VELO Backend -- Purchase Service (Phase 6.4, updated Phase 6.7 Batch 4)
# =============================================================================
#
# Double-entry purchase logic for booking flow.
#
# CREATE PURCHASE (called from create_booking + confirm_waitlist):
#   1. FOR UPDATE on user (balance check, P-07)
#   2. Calculate discount if promo applied.
#   3. Double-entry ledger (varies by promo type):
#      - No promo:     user_ledger(-price) + master_ledger(+price, frozen)
#      - Master promo: user_ledger(-paid)  + master_ledger(+paid, frozen)
#      - Company promo: user_ledger(-paid) + master_ledger(+price, frozen)
#                       + company_ledger(-discount, marketing)
#   4. Atomic increment promo used_count (P-07).
#   5. Create Purchase (amount_cents, discount_cents, paid_cents, promo_id).
#   6. Link booking.purchase_id.
#   7. Audit: purchase_created.
#
# FINALIZE PURCHASES (called from finalize_practice):
#   1. Unfreeze master_ledger entries (UPDATE is_frozen=False)
#   2. Commission = paid_cents * commission_percent // 100
#      (commission on live money only -- promo discount excluded)
#   3. Double-entry: master_ledger(-commission) + company_ledger(+commission)
#   4. Purchase -> completed
#
# LIST USER PURCHASES (Frontend Backlog):
#   Read-only paginated list with practice JOIN for display.
#
# INVARIANTS:
#   - Every Booking has exactly one Purchase (Semaphore 1.1/1.2)
#   - Every Purchase creates paired ledger entries (Semaphore 2.1)
#   - Free practices: paid_cents=0, ledger entries with amount=0
#   - Commission entries created even when commission=0 (double-entry)
#   - paid_cents = amount_cents - discount_cents
#   - SUM(user_ledger + master_ledger + company_ledger) = 0 always
#
# SESSION RULES:
#   No session.commit() (P-01). Caller manages transaction.
# =============================================================================

from datetime import datetime, timezone
from uuid import UUID

import structlog
from sqlalchemy import func, select, update
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
from app.modules.promos.models import Promo, PromoType
from app.modules.promos.validation import (
    calculate_discount,
    increment_promo_usage,
)
from app.modules.users.models import User

logger = structlog.get_logger()


async def create_purchase_for_booking(
    *,
    booking: Booking,
    practice: Practice,
    user: User,
    session: AsyncSession,
    promo: Promo | None = None,
) -> Purchase:
    """Create a Purchase linked to a Booking with double-entry ledger.

    Called from create_booking and confirm_waitlist. Always creates
    ledger entries -- even for free practices (amount_cents=0).

    Three ledger patterns depending on promo type:

    NO PROMO:
        user_ledger:   -price_cents (debit)
        master_ledger: +price_cents (credit, frozen)

    MASTER PROMO (master absorbs discount):
        user_ledger:   -paid_cents (debit, reduced)
        master_ledger: +paid_cents (credit, frozen, reduced)

    COMPANY PROMO (company pays from marketing budget):
        user_ledger:    -paid_cents     (debit, reduced)
        master_ledger:  +amount_cents   (credit, frozen, FULL price)
        company_ledger: -discount_cents (marketing expense)

    Args:
        booking: Already-created Booking (flushed, has id).
        practice: Practice being purchased (already loaded with FOR UPDATE).
        user: Buyer (current user).
        session: Active async session (caller manages transaction).
        promo: Optional validated Promo to apply.

    Returns:
        The created Purchase.

    Raises:
        BadRequestError: If user balance is insufficient.
        ConflictError: If promo usage race condition occurs.
    """
    price_cents = practice.price_cents  # 0 for free practices.

    # Calculate amounts based on promo.
    if promo:
        amount_cents, discount_cents, paid_cents = calculate_discount(
            promo, price_cents,
        )
    else:
        amount_cents = price_cents
        discount_cents = 0
        paid_cents = price_cents

    # Build reason suffix for ledger entries.
    reason_suffix = f"practice={practice.id}"
    if promo:
        reason_suffix += f",promo:{promo.code}"

    # FOR UPDATE on user row -- serialize concurrent purchases (P-07).
    user_locked = await session.get(User, user.id, with_for_update=True)
    # F-03: unique code so frontend can switch on e.code instead of
    # string-matching the human-readable message.
    if user_locked.balance_cents < paid_cents:
        raise BadRequestError("Insufficient balance", code="insufficient_balance")

    # Double-entry: user debit (what user actually pays).
    await record_user_ledger(
        user_id=user.id,
        amount_cents=-paid_cents,
        reason=f"purchase:{reason_suffix}",
        session=session,
    )

    # Double-entry: master credit (depends on promo type).
    if promo and promo.type == PromoType.COMPANY.value:
        # Company promo: master gets FULL price (company covers gap).
        master_credit = amount_cents
    else:
        # No promo or master promo: master gets what user paid.
        master_credit = paid_cents

    await record_master_ledger(
        user_id=practice.master_id,
        amount_cents=master_credit,
        reason=f"sale:{reason_suffix}",
        is_frozen=True,
        practice_id=practice.id,
        session=session,
    )

    # Company promo: company pays the discount from marketing budget.
    if promo and promo.type == PromoType.COMPANY.value and discount_cents > 0:
        await record_company_ledger(
            amount_cents=-discount_cents,
            ledger_type=CompanyLedgerType.MARKETING.value,
            reason=f"promo:{promo.code},{reason_suffix}",
            session=session,
        )

    # Atomic promo usage increment (P-07).
    if promo:
        await increment_promo_usage(promo_id=promo.id, session=session)

    # Create Purchase record.
    purchase = Purchase(
        user_id=user.id,
        practice_id=practice.id,
        booking_id=booking.id,
        promo_id=promo.id if promo else None,
        amount_cents=amount_cents,
        discount_cents=discount_cents,
        paid_cents=paid_cents,
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
            "amount_cents": amount_cents,
            "discount_cents": discount_cents,
            "paid_cents": paid_cents,
            "promo_code": promo.code if promo else None,
            "promo_type": promo.type if promo else None,
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
        amount_cents=amount_cents,
        discount_cents=discount_cents,
        paid_cents=paid_cents,
        promo_code=promo.code if promo else None,
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
    2. Calculate commission (paid_cents * commission_percent // 100)
    3. Double-entry: master_ledger(-commission) + company_ledger(+commission)
    4. Mark purchase as completed

    Commission is ALWAYS based on paid_cents (live money from user).
    Promo discounts do not generate commission.

    Even for free purchases (paid_cents=0), commission entries are
    created with amount=0 to maintain double-entry invariant.

    Args:
        practice_id: Practice being finalized.
        practice: Practice object (already loaded with FOR UPDATE).
        session: Active async session (caller manages transaction).

    Returns:
        List of finalized Purchase objects.
    """
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
        # L-07 fix: pure integer math -- no float intermediate.
        # Commission on live money only (paid_cents, not amount_cents).
        commission = purchase.paid_cents * settings.commission_percent // 100

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
            actor_id=purchase.user_id,
            actor_type="user",
            target_type="purchase",
            target_id=purchase.id,
            data={
                "practice_id": str(practice_id),
                "paid_cents": purchase.paid_cents,
                "commission_cents": commission,
                "promo_id": str(purchase.promo_id) if purchase.promo_id else None,
            },
            session=session,
        )

        logger.info(
            "purchase_finalized",
            purchase_id=str(purchase.id),
            practice_id=str(practice_id),
            paid_cents=purchase.paid_cents,
            commission_cents=commission,
        )

    return purchases


async def list_user_purchases(
    user: User,
    session: AsyncSession,
    *,
    status_filter: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[tuple[Purchase, Practice]], int]:
    """List purchases for a user with practice details (paginated).

    Fix 2.5: count derived from base query subquery (B-05 pattern) instead
    of a separate count_base with duplicated filter clauses. Adding a new
    filter to base is sufficient -- total stays in sync automatically.

    Returns:
        Tuple of (list of (Purchase, Practice) pairs, total count).
    """
    from app.modules.practices.models import Practice

    base = (
        select(Purchase, Practice)
        .join(Practice, Purchase.practice_id == Practice.id)
        .where(Purchase.user_id == user.id)
    )

    if status_filter:
        base = base.where(Purchase.status == status_filter)

    # B-05: count via subquery -- filters applied once, no duplication.
    total = (
        await session.execute(
            select(func.count()).select_from(base.subquery())
        )
    ).scalar_one()

    items_stmt = (
        base
        .order_by(Purchase.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(items_stmt)
    rows = result.all()

    return [(row[0], row[1]) for row in rows], total
