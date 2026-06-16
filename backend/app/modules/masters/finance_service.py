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
# CALENDAR BOUNDS are computed in UTC. A master in another timezone sees the
# UTC calendar week/month -- an accepted MVP simplification (revisit with E7).
#
# SESSION RULES:
#   Read-only -- callers pass get_db_reader. No commit (P-01).
# =============================================================================

from datetime import UTC, datetime, timedelta
from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.payments.models import LedgerStatus, MasterLedger
from app.modules.users.models import User

logger = structlog.get_logger()


def _calendar_period_bounds(
    period: str, now: datetime,
) -> tuple[datetime, datetime, datetime]:
    """Return (current_start, current_end, prev_start) for a calendar period.

    current_end doubles as prev_end (periods are contiguous). Boundaries are
    UTC. `period` is "week" (Monday 00:00 .. next Monday) or "month"
    (1st 00:00 .. next 1st).
    """
    if period == "week":
        start = (now - timedelta(days=now.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0,
        )
        current_end = start + timedelta(weeks=1)
        prev_start = start - timedelta(weeks=1)
        return start, current_end, prev_start

    # month
    start = now.replace(
        day=1, hour=0, minute=0, second=0, microsecond=0,
    )
    if start.month == 12:
        current_end = start.replace(year=start.year + 1, month=1)
    else:
        current_end = start.replace(month=start.month + 1)
    if start.month == 1:
        prev_start = start.replace(year=start.year - 1, month=12)
    else:
        prev_start = start.replace(month=start.month - 1)
    return start, current_end, prev_start


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
    cur_start, cur_end, prev_start = _calendar_period_bounds(period, now)

    income = await _sum_titled_income(user_id, cur_start, cur_end, session)
    prev_income = await _sum_titled_income(
        user_id, prev_start, cur_start, session,
    )

    # delta_pct only when the previous period was net-positive. With prev <= 0
    # there is no meaningful base: prev == 0 divides by zero, and prev < 0
    # (refunds exceeded sales) would flip the sign through abs(). In both cases
    # we return null and let the client show "--" instead of a misleading %.
    if prev_income > 0:
        delta_pct: int | None = round((income - prev_income) / prev_income * 100)
    else:
        delta_pct = None

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
    base = (
        select(MasterLedger, User)
        .outerjoin(User, MasterLedger.counterparty_id == User.id)
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
        }
        for entry, counterparty in rows
    ]

    return items, total
