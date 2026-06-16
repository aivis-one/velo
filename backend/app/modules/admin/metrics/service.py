# =============================================================================
# VELO Backend -- Admin Metrics Service (E9 / 4a)
# =============================================================================
#
# Read-only engagement aggregates over bookings + practices + diary. Each
# metric is anchored on Practice.scheduled_at within a calendar period
# (week = Mon..next Mon, month = 1st..next 1st, UTC) -- "practices that
# happened this period".
#
# CHECK-IN: among attended bookings whose practice fell in the period, how many
#   had a check-in. rate = checked_in / total_records. Weekly series (7 daily
#   buckets for week, weekly buckets for month) + bottom-N low-check-in
#   practices. One query, bucketed in Python (cold admin path).
#
# FEEDBACK: among attended bookings in the period, how many left feedback.
#   rate = left_review / visited. distribution = bucketed counts of those
#   feedbacks (confused 1-3 / good 4-7 / fire 8-10).
#
# RETURN: total_users = unique users with an attended practice in the period;
#   returning = those who also attended BEFORE the period start; rate =
#   returning / total_users. top_users = users by all-time attended count desc.
#
# rate_pct is integer percent, 0 when the denominator is 0 (honest empty).
#
# SESSION RULES:
#   Read-only -- callers pass get_db_reader. No commit (P-01). ORM-only.
# =============================================================================

import math
from datetime import UTC, datetime, timedelta
from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.admin.metrics.schemas import (
    CheckinMetricResponse,
    FeedbackMetricResponse,
    LowCheckinPractice,
    FeedbackRatingDistribution,
    ReturnMetricResponse,
    SeriesPoint,
    TopUser,
)
from app.modules.bookings.models import Booking, BookingStatus
from app.modules.diary.models import Checkin, Feedback
from app.modules.practices.models import Practice
from app.modules.users.models import User

logger = structlog.get_logger()

# Rating buckets (mirror E1 / diary insights): confused 1-3, good 4-7, fire 8+.
_CONFUSED_MAX = 3
_GOOD_MAX = 7

# How many practices / users to surface in the low / top sections.
_LOW_LIMIT = 5
_TOP_LIMIT = 5


def _calendar_bounds(
    period: str, now: datetime,
) -> tuple[datetime, datetime, datetime]:
    """Return (start, end, prev_start) for a calendar period (UTC).

    week  -> Monday 00:00 .. next Monday; prev_start = previous Monday.
    month -> 1st 00:00 .. next 1st;       prev_start = previous month 1st.
    """
    if period == "week":
        start = (now - timedelta(days=now.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0,
        )
        return start, start + timedelta(weeks=1), start - timedelta(weeks=1)

    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if start.month == 12:
        end = start.replace(year=start.year + 1, month=1)
    else:
        end = start.replace(month=start.month + 1)
    if start.month == 1:
        prev_start = start.replace(year=start.year - 1, month=12)
    else:
        prev_start = start.replace(month=start.month - 1)
    return start, end, prev_start


def _pct(numerator: int, denominator: int) -> int:
    """Integer percent; 0 when the denominator is 0."""
    if denominator == 0:
        return 0
    return round(numerator / denominator * 100)


def _bucket_layout(
    period: str, start: datetime, end: datetime,
) -> tuple[int, int]:
    """Return (bucket_days, n_buckets) for the series.

    week -> 7 daily buckets; month -> weekly buckets spanning the month.
    """
    if period == "week":
        return 1, 7
    total_days = (end - start).days
    return 7, max(1, math.ceil(total_days / 7))


async def get_checkin_metric(
    period: str,
    session: AsyncSession,
) -> CheckinMetricResponse:
    """Check-in rate + weekly series + low-check-in practices for the period."""
    start, end, _prev = _calendar_bounds(period, datetime.now(UTC))
    bucket_days, n_buckets = _bucket_layout(period, start, end)

    # One row per attended booking in the period: practice, scheduled_at, and
    # whether it has a check-in (count > 0). Outer join + group keeps bookings
    # with no check-in.
    rows = (
        await session.execute(
            select(
                Practice.id,
                Practice.title,
                Practice.scheduled_at,
                Booking.id,
                func.count(Checkin.id),
            )
            .select_from(Booking)
            .join(Practice, Booking.practice_id == Practice.id)
            .outerjoin(Checkin, Checkin.booking_id == Booking.id)
            .where(
                Booking.status == BookingStatus.ATTENDED.value,
                Practice.scheduled_at >= start,
                Practice.scheduled_at < end,
            )
            .group_by(Booking.id, Practice.id)
        )
    ).all()

    total_records = len(rows)
    checked_in = sum(1 for *_rest, ci_count in rows if ci_count > 0)

    # Per-bucket totals for the series.
    bucket_total = [0] * n_buckets
    bucket_checked = [0] * n_buckets
    # Per-practice totals for the low-check-in section.
    per_practice: dict[UUID, dict] = {}

    for practice_id, title, scheduled_at, _booking_id, ci_count in rows:
        has_checkin = ci_count > 0

        idx = (scheduled_at - start).days // bucket_days
        idx = max(0, min(idx, n_buckets - 1))
        bucket_total[idx] += 1
        if has_checkin:
            bucket_checked[idx] += 1

        agg = per_practice.setdefault(
            practice_id, {"title": title, "total": 0, "checked": 0},
        )
        agg["total"] += 1
        if has_checkin:
            agg["checked"] += 1

    series = [
        SeriesPoint(
            label=(start + timedelta(days=i * bucket_days)).strftime("%d.%m"),
            value=_pct(bucket_checked[i], bucket_total[i]),
        )
        for i in range(n_buckets)
    ]

    low_sorted = sorted(
        per_practice.items(),
        key=lambda kv: (_pct(kv[1]["checked"], kv[1]["total"]), -kv[1]["total"]),
    )
    low_practices = [
        LowCheckinPractice(
            id=practice_id,
            title=agg["title"],
            checkin_rate_pct=_pct(agg["checked"], agg["total"]),
            total=agg["total"],
        )
        for practice_id, agg in low_sorted[:_LOW_LIMIT]
    ]

    return CheckinMetricResponse(
        rate_pct=_pct(checked_in, total_records),
        total_records=total_records,
        checked_in=checked_in,
        series=series,
        low_practices=low_practices,
    )


async def get_feedback_metric(
    period: str,
    session: AsyncSession,
) -> FeedbackMetricResponse:
    """Feedback rate + rating distribution for the period."""
    start, end, _prev = _calendar_bounds(period, datetime.now(UTC))

    # visited = attended bookings whose practice fell in the period.
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

    # Ratings of feedbacks tied to those SAME attended bookings. We join
    # Feedback -> Booking on (practice_id, user_id) and require the booking to
    # be attended, so every counted feedback corresponds to a visited booking
    # (W-3: left_review <= visited, rate_pct never exceeds 100%). The partial
    # unique index on bookings (practice_id, user_id WHERE not cancelled) means
    # at most one attended booking matches per feedback, so no double-counting.
    ratings = (
        await session.execute(
            select(Feedback.rating)
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
    ).scalars().all()

    fire = good = confused = 0
    for rating in ratings:
        if rating <= _CONFUSED_MAX:
            confused += 1
        elif rating <= _GOOD_MAX:
            good += 1
        else:
            fire += 1

    left_review = len(ratings)

    return FeedbackMetricResponse(
        rate_pct=_pct(left_review, visited),
        visited=visited,
        left_review=left_review,
        distribution=FeedbackRatingDistribution(
            fire=fire, good=good, confused=confused,
        ),
    )


async def get_return_metric(
    period: str,
    session: AsyncSession,
) -> ReturnMetricResponse:
    """Return rate + top loyal users for the period."""
    start, end, _prev = _calendar_bounds(period, datetime.now(UTC))

    # Unique users with an attended practice in the period.
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
        # Of those, who attended a practice BEFORE the period start.
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

    # Top loyal users by all-time attended count.
    top_rows = (
        await session.execute(
            select(User, func.count(Booking.id))
            .join(Booking, Booking.user_id == User.id)
            .join(Practice, Booking.practice_id == Practice.id)
            .where(Booking.status == BookingStatus.ATTENDED.value)
            .group_by(User.id)
            .order_by(func.count(Booking.id).desc(), User.id)
            .limit(_TOP_LIMIT)
        )
    ).all()

    top_users = [
        TopUser(
            id=user.id,
            name=_user_name(user),
            practices_count=count,
        )
        for user, count in top_rows
    ]

    return ReturnMetricResponse(
        rate_pct=_pct(returning, total_users),
        total_users=total_users,
        returning=returning,
        top_users=top_users,
    )


def _user_name(user: User) -> str:
    """Display name: first + last, else a neutral label."""
    name = " ".join(
        part for part in (user.first_name, user.last_name) if part
    ).strip()
    return name or "Участник"
