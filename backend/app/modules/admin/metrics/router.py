# =============================================================================
# VELO Backend -- Admin Metrics Router (E9 / 4a)
# =============================================================================
#
# Engagement metric drill-ins for the admin dashboard.
#
# ENDPOINTS:
#   GET /api/v1/admin/metrics/check-in   -- check-in rate + series + low list
#   GET /api/v1/admin/metrics/feedback   -- feedback rate + rating distribution
#   GET /api/v1/admin/metrics/return     -- return rate + top loyal users
#
# Each takes ?period=week|month (calendar, UTC).
#
# AUTH: get_current_admin on every endpoint.
# SESSION: get_db_reader -- all read-only.
# =============================================================================

from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_reader
from app.modules.admin.metrics.schemas import (
    CheckinMetricResponse,
    FeedbackMetricResponse,
    ReturnMetricResponse,
)
from app.modules.admin.metrics.service import (
    get_checkin_metric,
    get_feedback_metric,
    get_return_metric,
)
from app.modules.auth.dependencies import get_current_admin
from app.modules.users.models import User

router = APIRouter()


@router.get("/metrics/check-in", response_model=CheckinMetricResponse)
async def checkin_metric_endpoint(
    period: Literal["week", "month"] = Query(default="week"),
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_reader),
) -> CheckinMetricResponse:
    """Check-in rate, weekly series, and low-check-in practices."""
    return await get_checkin_metric(period, session)


@router.get("/metrics/feedback", response_model=FeedbackMetricResponse)
async def feedback_metric_endpoint(
    period: Literal["week", "month"] = Query(default="week"),
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_reader),
) -> FeedbackMetricResponse:
    """Feedback rate and rating distribution."""
    return await get_feedback_metric(period, session)


@router.get("/metrics/return", response_model=ReturnMetricResponse)
async def return_metric_endpoint(
    period: Literal["week", "month"] = Query(default="week"),
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_reader),
) -> ReturnMetricResponse:
    """Return rate and top loyal users."""
    return await get_return_metric(period, session)
