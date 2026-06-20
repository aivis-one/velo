# =============================================================================
# VELO Backend -- Admin Stats Overview Router (E7)
# =============================================================================
#
# ENDPOINT:
#   GET /api/v1/admin/stats/overview?period=week|month
#       -- period-scoped platform overview (growth counts, revenue,
#          engagement rates, pending-reports badge) in a single call.
#
# Sibling of the existing /admin/stats counters (left untouched). Both are
# exact static paths, so include order does not matter.
#
# AUTH: get_current_admin. SESSION: get_db_reader -- read-only.
# =============================================================================

from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_reader
from app.modules.admin.stats.overview_schemas import AdminStatsOverviewResponse
from app.modules.admin.stats.overview_service import get_admin_stats_overview
from app.modules.auth.dependencies import get_current_admin
from app.modules.users.models import User

router = APIRouter()


@router.get("/stats/overview", response_model=AdminStatsOverviewResponse)
async def stats_overview_endpoint(
    period: Literal["week", "month"] = Query(default="week"),
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_reader),
) -> AdminStatsOverviewResponse:
    """Period-scoped platform overview + deltas vs the previous period."""
    return await get_admin_stats_overview(period, session)
