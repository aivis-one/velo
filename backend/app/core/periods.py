# =============================================================================
# VELO Backend -- Calendar Period Bounds + Deltas (E7)
# =============================================================================
#
# Single source of truth for the period math used by period-scoped analytics
# (master stats, admin overview, and -- pending the E7 follow-up refactor --
# finance / metrics / revenue, which still carry their own copies).
#
# calendar_period_bounds(period, now) -> (cur_start, cur_end, prev_start):
#   week  -> Monday 00:00 .. next Monday;  prev_start = previous Monday.
#   month -> 1st 00:00 .. next 1st;        prev_start = previous month's 1st.
#
# All boundaries are timezone-aware UTC. cur_end doubles as prev_end (periods
# are contiguous), so the previous period is [prev_start, cur_start). A master
# or admin in another timezone sees the UTC calendar week/month -- an accepted
# MVP simplification (the TZ revisit flagged in finance is centralised here).
#
# period_delta_pct / rate_delta_pp encode the two delta conventions used by the
# dashboards:
#   - counts and money -> signed percent change (period_delta_pct), null when
#     the previous period was non-positive (S-1: avoids div-by-zero and the
#     sign flip abs() would introduce). The client renders "--".
#   - rates (already a percent) -> simple point spread (rate_delta_pp); a
#     percent change of a percent would mislead.
# =============================================================================

from datetime import datetime, timedelta


def calendar_period_bounds(
    period: str, now: datetime,
) -> tuple[datetime, datetime, datetime]:
    """Return (cur_start, cur_end, prev_start) for a calendar period (UTC).

    week  -> Monday 00:00 .. next Monday; prev_start = previous Monday.
    month -> 1st 00:00 .. next 1st;       prev_start = previous month's 1st.

    cur_end doubles as prev_end (periods are contiguous): the previous period
    is [prev_start, cur_start). `now` is expected to be timezone-aware UTC.
    Any value other than "week" is treated as "month" (routers constrain the
    query param via Literal["week", "month"], so the service layer trusts it).
    """
    if period == "week":
        cur_start = (now - timedelta(days=now.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0,
        )
        cur_end = cur_start + timedelta(weeks=1)
        prev_start = cur_start - timedelta(weeks=1)
        return cur_start, cur_end, prev_start

    # month
    cur_start = now.replace(
        day=1, hour=0, minute=0, second=0, microsecond=0,
    )
    if cur_start.month == 12:
        cur_end = cur_start.replace(year=cur_start.year + 1, month=1)
    else:
        cur_end = cur_start.replace(month=cur_start.month + 1)
    if cur_start.month == 1:
        prev_start = cur_start.replace(year=cur_start.year - 1, month=12)
    else:
        prev_start = cur_start.replace(month=cur_start.month - 1)
    return cur_start, cur_end, prev_start


def shift_anchor(period: str, now: datetime, offset: int) -> datetime:
    """Shift `now` by `offset` whole periods (weeks or months).

    offset 0 -> now; -1 -> the previous week/month; +1 -> the next. Used by the
    admin-overview stepper: the returned anchor is fed to calendar_period_bounds,
    so the navigated period's delta is still measured against the period
    immediately before it. Pure date math -- default offset 0 is a no-op.
    """
    if offset == 0:
        return now
    if period == "week":
        return now + timedelta(weeks=offset)
    # month: shift year/month arithmetically; pin to day 1 to avoid day-overflow
    # (calendar_period_bounds re-pins day=1 anyway).
    total = now.year * 12 + (now.month - 1) + offset
    year, month0 = divmod(total, 12)
    return now.replace(year=year, month=month0 + 1, day=1)


def period_delta_pct(current: int, previous: int) -> int | None:
    """Signed percent change of `current` vs `previous`, or None.

    Returns None when `previous <= 0`: previous == 0 divides by zero, and a
    negative previous would flip the sign through the ratio. In both cases
    there is no meaningful base, so the client shows "--" instead of a
    misleading percentage (S-1 pattern, mirrors the E2 income delta).
    """
    if previous > 0:
        return round((current - previous) / previous * 100)
    return None


def rate_delta_pp(current_pct: int, previous_pct: int | None) -> int | None:
    """Difference in percentage POINTS (current - previous), or None.

    For rate metrics (check-in / feedback / return) both sides are already
    percentages, so we report the point spread rather than a percent change of
    a percent. None when there is no previous-period rate to compare against
    (e.g. the previous period had no denominator / activity).
    """
    if previous_pct is None:
        return None
    return current_pct - previous_pct
