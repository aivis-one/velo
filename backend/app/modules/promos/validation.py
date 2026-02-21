# =============================================================================
# VELO Backend -- Promo Validation (Phase 6.7, Batch 4)
# =============================================================================
#
# Shared validation logic for applying promo codes to purchases.
#
# validate_promo():
#   1. Lookup by code (case-insensitive, UPPER).
#   2. Check is_active.
#   3. Check validity window (valid_from <= now <= valid_until).
#   4. Check usage limit (used_count < max_uses).
#   5. Check first_purchase_only (no completed purchases for user).
#   6. Master promo scope: promo.master_id == practice.master_id.
#   7. Master promo practice scope: promo.practice_id == practice.id (if set).
#   8. Company promo: no scope restrictions (platform-wide).
#
# calculate_discount():
#   Pure function. price_cents * discount_percent // 100.
#   Returns (amount_cents, discount_cents, paid_cents).
#
# increment_promo_usage():
#   Atomic UPDATE ... SET used_count = used_count + 1
#   WHERE (max_uses IS NULL OR used_count < max_uses).
#   rows_affected = 0 -> race condition caught (P-07).
#
# SESSION RULES:
#   No session.commit() (P-01). Caller manages transaction.
# =============================================================================

from datetime import datetime, timezone
from uuid import UUID

import structlog
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestError, ConflictError
from app.modules.payments.models import Purchase, PurchaseStatus
from app.modules.practices.models import Practice
from app.modules.promos.models import Promo, PromoType

logger = structlog.get_logger()


async def validate_promo(
    *,
    code: str,
    practice: Practice,
    user_id: UUID,
    session: AsyncSession,
) -> Promo:
    """Validate a promo code for a specific practice and user.

    Does NOT increment used_count -- that happens atomically
    in increment_promo_usage() after ledger entries are created.

    Args:
        code: Promo code (will be uppercased for lookup).
        practice: Target practice (already loaded).
        user_id: Buyer's user ID.
        session: Active async session.

    Returns:
        The validated Promo object.

    Raises:
        BadRequestError: Invalid, expired, or inapplicable promo.
    """
    code_upper = code.strip().upper()

    # 1. Lookup by code.
    stmt = select(Promo).where(Promo.code == code_upper)
    result = await session.execute(stmt)
    promo = result.scalar_one_or_none()

    if not promo:
        raise BadRequestError(f"Promo code '{code_upper}' not found")

    # 2. Check active.
    if not promo.is_active:
        raise BadRequestError("Promo code is no longer active")

    # 3. Check validity window.
    now = datetime.now(timezone.utc)
    if promo.valid_from and now < promo.valid_from:
        raise BadRequestError("Promo code is not yet valid")
    if promo.valid_until and now > promo.valid_until:
        raise BadRequestError("Promo code has expired")

    # 4. Check usage limit (soft check -- atomic increment later).
    if promo.max_uses is not None and promo.used_count >= promo.max_uses:
        raise BadRequestError("Promo code has reached its usage limit")

    # 5. Check first_purchase_only.
    if promo.first_purchase_only:
        existing_stmt = (
            select(Purchase.id)
            .where(
                Purchase.user_id == user_id,
                Purchase.status.in_([
                PurchaseStatus.PENDING.value,
                PurchaseStatus.COMPLETED.value,
            ]),
            )
            .limit(1)
        )
        existing = (await session.execute(existing_stmt)).scalar_one_or_none()
        if existing is not None:
            raise BadRequestError(
                "Promo code is only valid for first purchase"
            )

    # 6-7. Scope checks based on promo type.
    if promo.type == PromoType.MASTER.value:
        # Master promo: must belong to the practice's master.
        if promo.master_id != practice.master_id:
            raise BadRequestError(
                "Promo code is not valid for this master's practices"
            )
        # Practice scope (if set).
        if promo.practice_id and promo.practice_id != practice.id:
            raise BadRequestError(
                "Promo code is not valid for this practice"
            )

    # 8. Company promo: no scope restrictions (platform-wide).

    logger.info(
        "promo_validated",
        code=code_upper,
        promo_id=str(promo.id),
        type=promo.type,
        discount_percent=promo.discount_percent,
        practice_id=str(practice.id),
        user_id=str(user_id),
    )

    return promo


def calculate_discount(
    promo: Promo,
    price_cents: int,
) -> tuple[int, int, int]:
    """Calculate discount amounts for a promo.

    Pure function -- no I/O, no side effects.

    Args:
        promo: Validated Promo object.
        price_cents: Full practice price in cents.

    Returns:
        Tuple of (amount_cents, discount_cents, paid_cents).
        Invariant: paid_cents = amount_cents - discount_cents.
    """
    amount_cents = price_cents
    discount_cents = price_cents * promo.discount_percent // 100
    paid_cents = amount_cents - discount_cents
    return amount_cents, discount_cents, paid_cents


async def increment_promo_usage(
    *,
    promo_id: UUID,
    session: AsyncSession,
) -> None:
    """Atomically increment promo used_count.

    Uses UPDATE ... WHERE (max_uses IS NULL OR used_count < max_uses)
    to prevent race conditions (P-07). If rows_affected = 0,
    another transaction consumed the last use.

    Args:
        promo_id: Promo to increment.
        session: Active async session.

    Raises:
        ConflictError: Race condition -- promo fully used by concurrent request.
    """
    stmt = (
        update(Promo)
        .where(
            Promo.id == promo_id,
            Promo.is_active.is_(True),
            # Atomic guard: only increment if under limit.
            (Promo.max_uses.is_(None)) | (Promo.used_count < Promo.max_uses),
        )
        .values(used_count=Promo.used_count + 1)
    )
    result = await session.execute(stmt)

    if result.rowcount == 0:
        raise ConflictError(
            "Promo code is no longer available (concurrent usage)"
        )

    logger.info(
        "promo_usage_incremented",
        promo_id=str(promo_id),
    )
