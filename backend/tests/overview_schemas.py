# =============================================================================
# VELO Backend -- Admin Stats Overview Schemas (E7)
# =============================================================================
#
# Period-scoped companion to the existing /admin/stats counters. Powers the
# admin dashboard's period block (Неделя/Месяц toggle was visual-only) in a
# single call, replacing the dashboard's previous fan-out across /admin/stats
# + /admin/revenue + the three /admin/metrics endpoints.
#
# All money is EUR cents; all figures are for the current calendar period
# (week|month, UTC) unless noted:
#   new_users / new_masters / practices_count -- entities created/scheduled in
#     the period, each with a signed percent delta vs the previous period
#     (period_delta_pct: null when the previous period was non-positive, S-1).
#   revenue_cents (+delta) / commission_cents -- GMV and platform cut, mirroring
#     the E9 revenue definitions.
#   *_rate_pct (+ *_rate_delta) -- engagement rates, mirroring the E9 metrics
#     definitions; the delta is in percentage POINTS (rate_delta_pp), null when
#     the previous period had no denominator.
#   pending_reports -- period-INDEPENDENT count of reports awaiting moderation
#     (lets the dashboard drop its second getReports call).
#
# Class names are Admin-prefixed to avoid OpenAPI component-name collisions.
# =============================================================================

from pydantic import BaseModel


class AdminStatsOverviewResponse(BaseModel):
    """GET /api/v1/admin/stats/overview?period=week|month."""

    # -- Growth counts (period) + deltas --
    new_users: int
    new_users_delta_pct: int | None
    new_masters: int
    new_masters_delta_pct: int | None
    practices_count: int
    practices_delta_pct: int | None

    # -- Revenue (period) --
    revenue_cents: int
    revenue_delta_pct: int | None
    commission_cents: int

    # -- Engagement rates (period) + point deltas --
    checkin_rate_pct: int
    checkin_rate_delta: int | None
    feedback_rate_pct: int
    feedback_rate_delta: int | None
    return_rate_pct: int
    return_rate_delta: int | None

    # -- Moderation (period-independent) --
    pending_reports: int
