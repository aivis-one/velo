# =============================================================================
# VELO Backend -- Master Stats Service (E7)
# =============================================================================
#
# Read-only period-scoped projection for the master dashboard stat grid.
# Counts are anchored on Practice.scheduled_at within a calendar period
# (week|month, UTC), each with a period-over-period delta.
#
#   practices_count    -- master's practices scheduled in the period, excluding
#                         draft / deleted / cancelled (real sessions that ran or
#                         are set to run this period).
#   participants_count -- DISTINCT users with an ATTENDED booking on those
#                         practices in the period.
#   income_cents       -- reused verbatim from the E2 finance projection
#                         (get_master_income): gross booked turnover for the
#                         period. Surfaced here for completeness so master stats
#                         and the finance screen share one income definition.
#
# DELTAS:
#   practices / participants -- period_delta_pct (signed %, null when the
#     previous period was non-positive -- S-1).
#   income -- delta_pct comes straight from get_master_income (same S-1 rule).
#
# CALENDAR BOUNDS come from core.periods (single source of truth, E7).
#
# SESSION RULES:
#   Read-only -- callers pass get_db_reader. No commit (P-01). ORM-only.
# =============================================================================

from datetime import UTC, datetime
from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.periods import calendar_period_bounds, period_delta_pct
from app.modules.bookings.models import Booking, BookingStatus
from app.modules.masters.finance_service import get_master_income
from app.modules.practices.models import Practice, PracticeStatus

logger = structlog.get_logger()

# Practices in these statuses are not period activity: drafts and soft-deletes
# never ran, and a cancelled practice did not take place. Mirrors the "real
# sessions" notion the master dashboard surfaces.
_NON_COUNTED_PRACTICE_STATUSES = (
    PracticeStatus.DRAFT.value,
    PracticeStatus.DELETED.value,
    PracticeStatus.CANCELLED.value,
)


async def _count_practices(
    user_id: UUID,
    start: datetime,
    end: datetime,
    session: AsyncSession,
) -> int:
    """Count the master's countable practices scheduled in [start, end)."""
    stmt = select(func.count(Practice.id)).where(
        Practice.master_id == user_id,
        Practice.status.notin_(_NON_COUNTED_PRACTICE_STATUSES),
        Practice.scheduled_at >= start,
        Practice.scheduled_at < end,
    )
    return (await session.execute(stmt)).scalar_one()


async def _count_participants(
    user_id: UUID,
    start: datetime,
    end: datetime,
    session: AsyncSession,
) -> int:
    """Count DISTINCT attendees across the master's practices in [start, end).

    A participant is a user with an ATTENDED booking on one of this master's
    practices whose scheduled_at falls in the period. Counted distinctly, so a
    user attending several of the master's practices in the period counts once.
    """
    stmt = (
        select(func.count(func.distinct(Booking.user_id)))
        .select_from(Booking)
        .join(Practice, Booking.practice_id == Practice.id)
        .where(
            Practice.master_id == user_id,
            Booking.status == BookingStatus.ATTENDED.value,
            Practice.scheduled_at >= start,
            Practice.scheduled_at < end,
        )
    )
    return (await session.execute(stmt)).scalar_one()


async def get_master_stats(
    user_id: UUID,
    period: str,
    session: AsyncSession,
) -> dict:
    """Period-scoped master stats + deltas. Returns a dict for MasterStatsResponse.

    practices_count / participants_count are anchored on Practice.scheduled_at
    in the current calendar period; their deltas compare against the previous
    period. income_cents / income_delta_pct are reused from the E2 finance
    projection so master stats and the finance screen never disagree on what
    "income" means.
    """
    now = datetime.now(UTC)
    cur_start, cur_end, prev_start = calendar_period_bounds(period, now)

    practices = await _count_practices(user_id, cur_start, cur_end, session)
    prev_practices = await _count_practices(
        user_id, prev_start, cur_start, session,
    )

    participants = await _count_participants(
        user_id, cur_start, cur_end, session,
    )
    prev_participants = await _count_participants(
        user_id, prev_start, cur_start, session,
    )

    # Income comes from the E2 finance projection. It computes its own
    # (identical) bounds internally; the E7 follow-up refactor collapses those
    # onto core.periods too.
    income = await get_master_income(user_id, period, session)

    return {
        "practices_count": practices,
        "practices_delta_pct": period_delta_pct(practices, prev_practices),
        "participants_count": participants,
        "participants_delta_pct": period_delta_pct(
            participants, prev_participants,
        ),
        "income_cents": income["income_cents"],
        "income_delta_pct": income["delta_pct"],
    }
