# =============================================================================
# VELO Backend -- Report Router (Phase 3.3)
# =============================================================================
#
# User-facing endpoints for reports (complaints).
#
# ENDPOINTS:
#   POST  /api/v1/reports          -- create a report (or get existing)
#   PATCH /api/v1/reports/{id}     -- edit own pending report
#   GET   /api/v1/reports/me       -- list own reports
#
# AUTH: get_current_user on all endpoints.
#
# DUPLICATE HANDLING:
#   POST returns 200 + ExistingReportResponse if user already reported
#   the same target. User can then PATCH to update the reason.
# =============================================================================

from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_reader, get_db_session
from app.modules.auth.dependencies import get_current_user
from app.modules.reports.models import Report
from app.modules.reports.schemas import (
    CreateReportRequest,
    ExistingReportResponse,
    ReportResponse,
    UpdateReportRequest,
)
from app.modules.reports.service import (
    create_report,
    get_existing_report,
    update_report,
)
from app.modules.users.models import User

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


@router.post("")
async def create_report_endpoint(
    body: CreateReportRequest,
    response: Response,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> ReportResponse | ExistingReportResponse:
    """Create a new report. Returns existing report (200) if duplicate."""
    report = await create_report(
        user=user,
        target_type=body.target_type,
        target_id=body.target_id,
        reason=body.reason,
        session=session,
    )

    if report is None:
        # Duplicate found -- return existing report with 200.
        existing = await get_existing_report(
            user=user,
            target_type=body.target_type,
            target_id=body.target_id,
            session=session,
        )
        response.status_code = status.HTTP_200_OK
        return ExistingReportResponse(
            report=ReportResponse.model_validate(existing, from_attributes=True),
        )

    await session.flush()
    await session.refresh(report)

    response.status_code = status.HTTP_201_CREATED
    return ReportResponse.model_validate(report, from_attributes=True)


@router.patch("/{report_id}", response_model=ReportResponse)
async def update_report_endpoint(
    report_id: UUID,
    body: UpdateReportRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> ReportResponse:
    """Edit own pending report (reason only)."""
    report = await update_report(
        report_id=report_id,
        user=user,
        reason=body.reason,
        session=session,
    )
    await session.flush()
    await session.refresh(report)

    return ReportResponse.model_validate(report, from_attributes=True)


@router.get("/me", response_model=list[ReportResponse])
async def get_my_reports(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_reader),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[ReportResponse]:
    """List current user's reports."""
    stmt = (
        select(Report)
        .where(Report.reporter_id == user.id)
        .order_by(Report.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(stmt)
    reports = result.scalars().all()

    return [
        ReportResponse.model_validate(r, from_attributes=True)
        for r in reports
    ]
