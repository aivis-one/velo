# =============================================================================
# VELO Backend -- Master Finance Service (E2)
# =============================================================================
#
# Read-only projections over master_ledger for the master finance/analytics
# screens. No migration logic here -- columns are added by the E2 migration and
# tagged at write time by record_master_ledger(title=..., counterparty_id=...).
#
# INCOME (GET /masters/me/income?period):
#   income_cents = SUM(amount_cents) of title-tagged DONE rows in the current
#   calendar period (week = Mon..next Mon, month = 1st..next 1st, UTC). This is
#   the master's GROSS BOOKED TURNOVER for the period -- the signed sum of the
#   same title-tagged movements the transaction feed shows: sale (+),
#   commission (-), refund (-). It is deliberately NOT realized earnings:
#   - sale credits are counted even while still frozen (practice not yet
#     finalized), so the figure matches the feed the master sees;
#   - a refund is booked in the period it happens, so a sale in one period and
#     its refund in the next leave the earlier period's turnover unreduced.
#   For realized/available earnings use the ledger balances, not this endpoint.
#   delta_pct compares against the previous calendar period; null when the
#   previous period had no net-positive turnover.
#
# TRANSACTIONS (GET /masters/me/transactions):
#   Title-tagged DONE rows, newest first, paginated. counterparty_name is
#   resolved via an outer join to users (null for platform-side rows).
#
# CALENDAR BOUNDS + the income delta come from core.periods (single source of
# truth, E7): calendar_period_bounds gives the UTC week/month boundaries and
# period_delta_pct encodes the S-1 rule. A master in another timezone sees the
# UTC calendar week/month -- an accepted MVP simplification.
#
# SESSION RULES:
#   Read-only -- callers pass get_db_reader. No commit (P-01).
# =============================================================================

from datetime import UTC, datetime
from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.periods import calendar_period_bounds, period_delta_pct
from app.modules.payments.models import LedgerStatus, MasterLedger
from app.modules.practices.models import Practice
from app.modules.users.models import User

logger = structlog.get_logger()


async def _sum_titled_income(
    user_id: UUID,
    start: datetime,
    end: datetime,
    session: AsyncSession,
) -> int:
    """SUM(amount_cents) of title-tagged DONE rows in [start, end).

    Signed sum of the title-tagged movements (sale +, commission -, refund -):
    gross booked turnover, not realized earnings. Sale credits are included
    even while frozen, so this matches the master's transaction feed.
    """
    stmt = (
        select(func.coalesce(func.sum(MasterLedger.amount_cents), 0))
        .where(
            MasterLedger.user_id == user_id,
            MasterLedger.status == LedgerStatus.DONE.value,
            MasterLedger.title.isnot(None),
            MasterLedger.created_at >= start,
            MasterLedger.created_at < end,
        )
    )
    return (await session.execute(stmt)).scalar_one()


async def get_master_income(
    user_id: UUID,
    period: str,
    session: AsyncSession,
) -> dict:
    """Gross booked turnover for the current calendar period + delta vs prev.

    income_cents is the signed sum of title-tagged sale/commission/refund
    movements in the period (frozen sales included), matching the transaction
    feed -- not realized earnings. Returns a dict ready for IncomeResponse.
    """
    now = datetime.now(UTC)
    cur_start, cur_end, prev_start = calendar_period_bounds(period, now)

    income = await _sum_titled_income(user_id, cur_start, cur_end, session)
    prev_income = await _sum_titled_income(
        user_id, prev_start, cur_start, session,
    )

    # Signed percent change vs the previous period; null when prev <= 0 (S-1:
    # prev == 0 divides by zero, prev < 0 would flip the sign). Client shows
    # "--" in that case.
    delta_pct = period_delta_pct(income, prev_income)

    return {
        "income_cents": income,
        "prev_income_cents": prev_income,
        "delta_pct": delta_pct,
    }


def _counterparty_name(user: User | None) -> str | None:
    """Display name for a transaction counterparty, or None for platform rows.

    Never falls back to a raw id (mirrors the reviews projection): an existing
    counterparty with no name renders as a neutral participant label.
    """
    if user is None:
        return None
    name = " ".join(
        part for part in (user.first_name, user.last_name) if part
    ).strip()
    return name or "Участник"


async def list_master_transactions(
    user_id: UUID,
    session: AsyncSession,
    *,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[dict], int]:
    """List the master's title-tagged transactions (newest first, paginated).

    Returns (items, total). Each item is a dict ready for MasterTransactionItem.
    """
    # M5: outerjoin Practice on the ledger row's practice_id (nullable, SET NULL)
    # so the feed can show the practice NAME instead of the generic stored title.
    # practice_title is None when the row has no practice_id or the practice was
    # deleted. The join is 1:1 (practice_id FK), so it never multiplies rows.
    base = (
        select(MasterLedger, User, Practice.title)
        .outerjoin(User, MasterLedger.counterparty_id == User.id)
        .outerjoin(Practice, MasterLedger.practice_id == Practice.id)
        .where(
            MasterLedger.user_id == user_id,
            MasterLedger.status == LedgerStatus.DONE.value,
            MasterLedger.title.isnot(None),
        )
    )

    total = (
        await session.execute(
            select(func.count()).select_from(base.subquery())
        )
    ).scalar_one()

    rows = (
        await session.execute(
            base.order_by(MasterLedger.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
    ).all()

    items = [
        {
            "title": entry.title,
            "created_at": entry.created_at,
            "counterparty_name": _counterparty_name(counterparty),
            "amount_cents": entry.amount_cents,
            "practice_title": practice_title,
        }
        for entry, counterparty, practice_title in rows
    ]

    return items, total
