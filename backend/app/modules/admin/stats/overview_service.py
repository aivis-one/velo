# =============================================================================
# VELO Backend -- Admin Stats Overview Service (E7)
# =============================================================================
#
# Read-only period-scoped platform overview for the admin dashboard. One call
# returns growth counts, revenue, engagement rates, and the pending-reports
# badge, each (except pending_reports) for the current calendar period with a
# period-over-period delta.
#
# DEFINITIONS (reused, not reinvented):
#   new_users / new_masters -- users (role==MASTER for the latter) whose
#     created_at falls in the period. "new_masters" tracks account-registration
#     date, symmetric with new_users (agreed convention; there is no clean
#     "became master at" timestamp).
#   practices_count -- platform practices scheduled in the period, excluding
#     draft / deleted / cancelled (same exclusion as master stats, E7).
#   revenue_cents / commission_cents -- GMV (completed Purchase.paid_cents) and
#     platform cut (CompanyLedger COMMISSION), mirroring admin revenue (E9/4b).
#   *_rate -- check-in / feedback / return, mirroring admin metrics (E9/4a),
#     anchored on Practice.scheduled_at:
#       check-in : checked-in attended bookings / attended bookings.
#       feedback : feedbacks tied to attended bookings / attended bookings
#                  (W-3 join keeps the rate <= 100%).
#       return   : period attendees who also attended before the period start
#                  / period attendees.
#   pending_reports -- COUNT(reports WHERE status=pending), period-independent.
#
# DELTAS:
#   counts / revenue -> period_delta_pct (signed %, null when prev <= 0, S-1).
#   rates -> rate_delta_pp (percentage points, null when the previous period
#            had no denominator).
#
# CALENDAR BOUNDS come from core.periods (single source of truth, E7).
#
# SESSION RULES:
#   Read-only -- callers pass get_db_reader. No commit (P-01). ORM-only.
# =============================================================================

from datetime import UTC, datetime

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.periods import (
    calendar_period_bounds,
    period_delta_pct,
    rate_delta_pp,
)
from app.modules.admin.stats.overview_schemas import AdminStatsOverviewResponse
from app.modules.bookings.models import Booking, BookingStatus
from app.modules.diary.models import Checkin, Feedback
from app.modules.payments.models import (
    CompanyLedger,
    CompanyLedgerType,
    LedgerStatus,
    Purchase,
    PurchaseStatus,
)
from app.modules.practices.models import Practice, PracticeStatus
from app.modules.reports.models import Report, ReportStatus
from app.modules.users.models import User, UserRole

logger = structlog.get_logger()

# Practices in these statuses are not period activity (mirror master stats).
_HIDDEN_PRACTICE_STATUSES = (
    PracticeStatus.DRAFT.value,
    PracticeStatus.DELETED.value,
    PracticeStatus.CANCELLED.value,
)


def _pct(numerator: int, denominator: int) -> int:
    """Integer percent; 0 when the denominator is 0 (mirrors admin metrics)."""
    if denominator == 0:
        return 0
    return round(numerator / denominator * 100)


# ---------------------------------------------------------------------------
# Growth counts
# ---------------------------------------------------------------------------
async def _count_new_users(
    start: datetime, end: datetime, session: AsyncSession,
) -> int:
    """Users registered in [start, end)."""
    stmt = select(func.count(User.id)).where(
        User.created_at >= start,
        User.created_at < end,
    )
    return (await session.execute(stmt)).scalar_one()


async def _count_new_masters(
    start: datetime, end: datetime, session: AsyncSession,
) -> int:
    """Master-role users registered in [start, end) (by account creation)."""
    stmt = select(func.count(User.id)).where(
        User.role == UserRole.MASTER,
        User.created_at >= start,
        User.created_at < end,
    )
    return (await session.execute(stmt)).scalar_one()


async def _count_practices(
    start: datetime, end: datetime, session: AsyncSession,
) -> int:
    """Platform practices scheduled in [start, end) (excludes hidden)."""
    stmt = select(func.count(Practice.id)).where(
        Practice.status.notin_(_HIDDEN_PRACTICE_STATUSES),
        Practice.scheduled_at >= start,
        Practice.scheduled_at < end,
    )
    return (await session.execute(stmt)).scalar_one()


# ---------------------------------------------------------------------------
# Revenue
# ---------------------------------------------------------------------------
async def _sum_revenue(
    start: datetime, end: datetime, session: AsyncSession,
) -> int:
    """GMV: SUM(paid_cents) of completed purchases completed in [start, end)."""
    stmt = select(func.coalesce(func.sum(Purchase.paid_cents), 0)).where(
        Purchase.status == PurchaseStatus.COMPLETED.value,
        Purchase.completed_at >= start,
        Purchase.completed_at < end,
    )
    return (await session.execute(stmt)).scalar_one()


async def _sum_commission(
    start: datetime, end: datetime, session: AsyncSession,
) -> int:
    """Platform commission booked into the company ledger in [start, end)."""
    stmt = select(func.coalesce(func.sum(CompanyLedger.amount_cents), 0)).where(
        CompanyLedger.type == CompanyLedgerType.COMMISSION.value,
        CompanyLedger.status == LedgerStatus.DONE.value,
        CompanyLedger.created_at >= start,
        CompanyLedger.created_at < end,
    )
    return (await session.execute(stmt)).scalar_one()


# ---------------------------------------------------------------------------
# Engagement rates -- each returns (numerator, denominator) for the period
# ---------------------------------------------------------------------------
async def _checkin_counts(
    start: datetime, end: datetime, session: AsyncSession,
) -> tuple[int, int]:
    """(checked_in, total_records) over attended bookings in [start, end)."""
    total = (
        await session.execute(
            select(func.count(Booking.id))
            .select_from(Booking)
            .join(Practice, Booking.practice_id == Practice.id)
            .where(
                Booking.status == BookingStatus.ATTENDED.value,
                Practice.scheduled_at >= start,
                Practice.scheduled_at < end,
            )
        )
    ).scalar_one()
    checked = (
        await session.execute(
            select(func.count(func.distinct(Booking.id)))
            .select_from(Booking)
            .join(Practice, Booking.practice_id == Practice.id)
            .join(Checkin, Checkin.booking_id == Booking.id)
            .where(
                Booking.status == BookingStatus.ATTENDED.value,
                Practice.scheduled_at >= start,
                Practice.scheduled_at < end,
            )
        )
    ).scalar_one()
    return checked, total


async def _feedback_counts(
    start: datetime, end: datetime, session: AsyncSession,
) -> tuple[int, int]:
    """(left_review, visited) over attended bookings in [start, end).

    left_review joins Feedback -> Booking on (practice_id, user_id) requiring
    the booking to be attended, so it never exceeds visited (W-3).
    """
    visited = (
        await session.execute(
            select(func.count(Booking.id))
            .select_from(Booking)
            .join(Practice, Booking.practice_id == Practice.id)
            .where(
                Booking.status == BookingStatus.ATTENDED.value,
                Practice.scheduled_at >= start,
                Practice.scheduled_at < end,
            )
        )
    ).scalar_one()
    left_review = (
        await session.execute(
            select(func.count())
            .select_from(Feedback)
            .join(Practice, Feedback.practice_id == Practice.id)
            .join(
                Booking,
                (Booking.practice_id == Feedback.practice_id)
                & (Booking.user_id == Feedback.user_id),
            )
            .where(
                Booking.status == BookingStatus.ATTENDED.value,
                Practice.scheduled_at >= start,
                Practice.scheduled_at < end,
            )
        )
    ).scalar_one()
    return left_review, visited


async def _return_counts(
    start: datetime, end: datetime, session: AsyncSession,
) -> tuple[int, int]:
    """(returning, total_users) over period attendees in [start, end).

    returning = period attendees who also attended a practice scheduled before
    the period start.
    """
    period_user_ids = set(
        (
            await session.execute(
                select(Booking.user_id)
                .join(Practice, Booking.practice_id == Practice.id)
                .where(
                    Booking.status == BookingStatus.ATTENDED.value,
                    Practice.scheduled_at >= start,
                    Practice.scheduled_at < end,
                )
                .distinct()
            )
        ).scalars().all()
    )
    total_users = len(period_user_ids)

    returning = 0
    if period_user_ids:
        prior_ids = set(
            (
                await session.execute(
                    select(Booking.user_id)
                    .join(Practice, Booking.practice_id == Practice.id)
                    .where(
                        Booking.status == BookingStatus.ATTENDED.value,
                        Practice.scheduled_at < start,
                        Booking.user_id.in_(period_user_ids),
                    )
                    .distinct()
                )
            ).scalars().all()
        )
        returning = len(prior_ids)
    return returning, total_users


def _rate_with_delta(
    cur: tuple[int, int], prev: tuple[int, int],
) -> tuple[int, int | None]:
    """Return (current_rate_pct, point_delta_vs_prev).

    The delta is None when the previous period had no denominator (no activity
    to compare against), so an empty prior period never shows a misleading
    jump from 0.
    """
    cur_num, cur_den = cur
    prev_num, prev_den = prev
    current_rate = _pct(cur_num, cur_den)
    prev_rate = _pct(prev_num, prev_den) if prev_den > 0 else None
    return current_rate, rate_delta_pp(current_rate, prev_rate)


async def get_admin_stats_overview(
    period: str,
    session: AsyncSession,
) -> AdminStatsOverviewResponse:
    """Period-scoped platform overview + deltas for the admin dashboard."""
    now = datetime.now(UTC)
    cur_start, cur_end, prev_start = calendar_period_bounds(period, now)

    # -- growth counts (current + previous) --
    new_users = await _count_new_users(cur_start, cur_end, session)
    prev_new_users = await _count_new_users(prev_start, cur_start, session)
    new_masters = await _count_new_masters(cur_start, cur_end, session)
    prev_new_masters = await _count_new_masters(prev_start, cur_start, session)
    practices = await _count_practices(cur_start, cur_end, session)
    prev_practices = await _count_practices(prev_start, cur_start, session)

    # -- revenue (current + previous) + commission (current) --
    revenue = await _sum_revenue(cur_start, cur_end, session)
    prev_revenue = await _sum_revenue(prev_start, cur_start, session)
    commission = await _sum_commission(cur_start, cur_end, session)

    # -- engagement rates (current + previous) --
    checkin_rate, checkin_delta = _rate_with_delta(
        await _checkin_counts(cur_start, cur_end, session),
        await _checkin_counts(prev_start, cur_start, session),
    )
    feedback_rate, feedback_delta = _rate_with_delta(
        await _feedback_counts(cur_start, cur_end, session),
        await _feedback_counts(prev_start, cur_start, session),
    )
    return_rate, return_delta = _rate_with_delta(
        await _return_counts(cur_start, cur_end, session),
        await _return_counts(prev_start, cur_start, session),
    )

    # -- moderation (period-independent) --
    pending_reports = (
        await session.execute(
            select(func.count(Report.id)).where(
                Report.status == ReportStatus.PENDING.value,
            )
        )
    ).scalar_one()

    return AdminStatsOverviewResponse(
        new_users=new_users,
        new_users_delta_pct=period_delta_pct(new_users, prev_new_users),
        new_masters=new_masters,
        new_masters_delta_pct=period_delta_pct(new_masters, prev_new_masters),
        practices_count=practices,
        practices_delta_pct=period_delta_pct(practices, prev_practices),
        revenue_cents=revenue,
        revenue_delta_pct=period_delta_pct(revenue, prev_revenue),
        commission_cents=commission,
        checkin_rate_pct=checkin_rate,
        checkin_rate_delta=checkin_delta,
        feedback_rate_pct=feedback_rate,
        feedback_rate_delta=feedback_delta,
        return_rate_pct=return_rate,
        return_rate_delta=return_delta,
        pending_reports=pending_reports,
    )
