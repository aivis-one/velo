# =============================================================================
# VELO Backend — Payment Service (Phase 6.2)
# =============================================================================
#
# Ledger recording functions with automatic balance recalculation.
#
# PATTERN:
#   1. Create ledger entry → session.add()
#   2. Flush (get DB-generated defaults)
#   3. SELECT SUM() with FOR UPDATE on owner row
#   4. Update cached balance field
#
# WHY NOT SQLAlchemy event listeners?
#   @event.listens_for is synchronous. In async context (asyncpg)
#   it cannot execute queries. Explicit service functions are the
#   correct approach for async ORMs. See VELO-LLM-Code-Review-Guide.
#
# SESSION RULES:
#   No session.commit() (P-01). Caller's session handles transaction.
#   All ledger + balance updates happen in the SAME transaction.
#
# CONCURRENCY:
#   Balance recalculation uses with_for_update() on the owner row
#   (User / MasterProfile) to prevent concurrent writes from
#   producing inconsistent cached balances (P-07).
# =============================================================================

from uuid import UUID

import structlog
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.modules.masters.models import MasterProfile
from app.modules.payments.models import (
    CompanyLedger,
    CompanyLedgerType,
    LedgerStatus,
    MasterLedger,
    UserLedger,
)
from app.modules.users.models import User

logger = structlog.get_logger()


async def record_user_ledger(
    *,
    user_id: UUID,
    amount_cents: int,
    reason: str,
    session: AsyncSession,
    status: str = LedgerStatus.DONE.value,
    notes: str | None = None,
) -> UserLedger:
    """Record a user ledger entry and recalculate cached balance.

    Args:
        user_id: Owner of the wallet.
        amount_cents: Positive = credit, negative = debit.
        reason: Machine-readable reason (e.g. "purchase:practice=456").
        session: Active async session (caller manages transaction).
        status: Ledger status (default: "done").
        notes: Optional human-readable notes.

    Returns:
        The created UserLedger entry.
    """
    entry = UserLedger(
        user_id=user_id,
        amount_cents=amount_cents,
        status=status,
        reason=reason,
        notes=notes,
    )
    session.add(entry)
    await session.flush()

    # Recalculate cached balance with row lock (P-07).
    user = await session.get(
        User, user_id, with_for_update=True,
    )
    balance = await _sum_user_balance(user_id, session)
    # Bypass __setattr__ guard — this IS the legitimate updater.
    object.__setattr__(user, "balance_cents", balance)
    flag_modified(user, "balance_cents")

    logger.info(
        "user_ledger_recorded",
        user_id=str(user_id),
        amount_cents=amount_cents,
        reason=reason,
        new_balance=balance,
    )

    return entry


async def record_master_ledger(
    *,
    user_id: UUID,
    amount_cents: int,
    reason: str,
    session: AsyncSession,
    is_frozen: bool = True,
    practice_id: UUID | None = None,
    status: str = LedgerStatus.DONE.value,
    notes: str | None = None,
) -> MasterLedger:
    """Record a master ledger entry and recalculate cached balances.

    Args:
        user_id: Master's user_id.
        amount_cents: Positive = credit, negative = debit.
        reason: Machine-readable reason (e.g. "sale:practice=456").
        session: Active async session (caller manages transaction).
        is_frozen: True = locked until practice completes.
        practice_id: Associated practice (for frozen tracking).
        status: Ledger status (default: "done").
        notes: Optional human-readable notes.

    Returns:
        The created MasterLedger entry.
    """
    entry = MasterLedger(
        user_id=user_id,
        amount_cents=amount_cents,
        is_frozen=is_frozen,
        status=status,
        reason=reason,
        practice_id=practice_id,
        notes=notes,
    )
    session.add(entry)
    await session.flush()

    # Recalculate both cached fields with row lock (P-07).
    profile = await session.get(
        MasterProfile, user_id, with_for_update=True,
    )
    frozen, available = await _sum_master_balances(user_id, session)
    # Bypass __setattr__ guard — this IS the legitimate updater.
    object.__setattr__(profile, "frozen_cents", frozen)
    flag_modified(profile, "frozen_cents")
    object.__setattr__(profile, "available_cents", available)
    flag_modified(profile, "available_cents")

    logger.info(
        "master_ledger_recorded",
        user_id=str(user_id),
        amount_cents=amount_cents,
        is_frozen=is_frozen,
        reason=reason,
        new_frozen=frozen,
        new_available=available,
    )

    return entry


async def record_company_ledger(
    *,
    amount_cents: int,
    ledger_type: str,
    reason: str,
    session: AsyncSession,
    reference_id: UUID | None = None,
    status: str = LedgerStatus.DONE.value,
) -> CompanyLedger:
    """Record a company ledger entry.

    No cached balance to update — company has no profile row.

    Args:
        amount_cents: Positive = revenue, negative = expense.
        ledger_type: One of CompanyLedgerType values.
        reason: Machine-readable reason.
        session: Active async session (caller manages transaction).
        reference_id: UUID of related purchase/withdrawal.
        status: Ledger status (default: "done").

    Returns:
        The created CompanyLedger entry.
    """
    entry = CompanyLedger(
        amount_cents=amount_cents,
        type=ledger_type,
        status=status,
        reason=reason,
        reference_id=reference_id,
    )
    session.add(entry)
    await session.flush()

    logger.info(
        "company_ledger_recorded",
        amount_cents=amount_cents,
        ledger_type=ledger_type,
        reason=reason,
        reference_id=str(reference_id) if reference_id else None,
    )

    return entry


# -- Internal helpers --------------------------------------------------------


async def _sum_user_balance(
    user_id: UUID, session: AsyncSession,
) -> int:
    """SUM(amount_cents) WHERE user_id=X AND status='done'."""
    stmt = (
        select(func.coalesce(func.sum(UserLedger.amount_cents), 0))
        .where(
            UserLedger.user_id == user_id,
            UserLedger.status == LedgerStatus.DONE.value,
        )
    )
    result = await session.execute(stmt)
    return result.scalar_one()


async def _sum_master_balances(
    user_id: UUID, session: AsyncSession,
) -> tuple[int, int]:
    """Calculate frozen and available sums in one query.

    Returns:
        (frozen_cents, available_cents) tuple.
    """
    stmt = select(
        func.coalesce(
            func.sum(
                case(
                    (MasterLedger.is_frozen.is_(True), MasterLedger.amount_cents),
                    else_=0,
                )
            ),
            0,
        ).label("frozen"),
        func.coalesce(
            func.sum(
                case(
                    (MasterLedger.is_frozen.is_(False), MasterLedger.amount_cents),
                    else_=0,
                )
            ),
            0,
        ).label("available"),
    ).where(
        MasterLedger.user_id == user_id,
        MasterLedger.status == LedgerStatus.DONE.value,
    )
    result = await session.execute(stmt)
    row = result.one()
    return row.frozen, row.available
