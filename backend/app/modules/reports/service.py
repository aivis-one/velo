# =============================================================================
# VELO Backend -- Report Service (Phase 3.3, updated Phase 4.1)
# =============================================================================
#
# User-facing business logic for reports (complaints).
#
# CREATE FLOW:
#   1. Validate target exists (user/master/practice)
#   2. Check for duplicate (same reporter + target)
#   3. If duplicate exists -- return it (caller shows "edit instead")
#   4. If no duplicate -- create new report with status=pending
#
# UPDATE FLOW:
#   1. Load report by id with FOR UPDATE, verify ownership
#   2. Verify status == pending (can't edit resolved/dismissed)
#   3. Update reason
#
# TARGET VALIDATION:
#   - user: SELECT from users WHERE id = target_id
#   - master: SELECT from master_profiles WHERE user_id = target_id
#   - practice: SELECT from practices WHERE id = target_id
#
# SESSION RULES:
#   No session.commit() here (P-01).
#   create_report() calls flush() internally to catch IntegrityError (P-05).
#   update_report() relies on router for flush + refresh.
# =============================================================================

from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestError, NotFoundError
from app.modules.masters.models import MasterProfile
from app.modules.practices.models import Practice
from app.modules.reports.models import Report, ReportStatus, ReportTargetType
from app.modules.users.models import User

logger = structlog.get_logger()


async def _validate_target(
    target_type: str,
    target_id: UUID,
    session: AsyncSession,
) -> None:
    """Validate that the report target exists in the database.

    Raises BadRequestError if target_type is invalid.
    Raises NotFoundError if target does not exist.
    """
    tt = ReportTargetType(target_type)

    if tt == ReportTargetType.USER:
        result = await session.execute(
            select(User.id).where(User.id == target_id)
        )
        if not result.scalar_one_or_none():
            raise NotFoundError("Target user not found")

    elif tt == ReportTargetType.MASTER:
        result = await session.execute(
            select(MasterProfile.user_id).where(
                MasterProfile.user_id == target_id
            )
        )
        if not result.scalar_one_or_none():
            raise NotFoundError("Target master not found")

    elif tt == ReportTargetType.PRACTICE:
        result = await session.execute(
            select(Practice.id).where(Practice.id == target_id)
        )
        if not result.scalar_one_or_none():
            raise NotFoundError("Target practice not found")


async def create_report(
    user: User,
    target_type: str,
    target_id: UUID,
    reason: str,
    session: AsyncSession,
) -> Report | None:
    """Create a new report or return None if duplicate exists.

    Returns:
        Report -- newly created report.
        None   -- if a duplicate exists (caller should return the existing one).
    """
    # -- Validate target exists --
    await _validate_target(target_type, target_id, session)

    # -- Prevent self-reporting --
    # For "user" target_type, target_id is user.id directly.
    # For "master" target_type, target_id is also user_id
    # (FK in master_profiles).
    if (
        target_type in (ReportTargetType.USER, ReportTargetType.MASTER)
        and target_id == user.id
    ):
        raise BadRequestError("Cannot report yourself")

    # -- Check for duplicate --
    existing = await _find_existing_report(user.id, target_type, target_id, session)
    if existing:
        logger.info(
            "report_duplicate_found",
            reporter_id=str(user.id),
            target_type=target_type,
            target_id=str(target_id),
            existing_report_id=str(existing.id),
        )
        return None

    # -- Create report --
    report = Report(
        reporter_id=user.id,
        target_type=target_type,
        target_id=target_id,
        reason=reason,
        status=ReportStatus.PENDING.value,
    )
    session.add(report)

    try:
        async with session.begin_nested():
            await session.flush()
    except IntegrityError:
        # Race condition: another request inserted the same report
        # between our SELECT and INSERT. Return None so caller
        # treats it as a duplicate (same as the normal path).
        logger.info(
            "report_duplicate_race",
            reporter_id=str(user.id),
            target_type=target_type,
            target_id=str(target_id),
        )
        return None

    logger.info(
        "report_created",
        reporter_id=str(user.id),
        target_type=target_type,
        target_id=str(target_id),
    )

    return report


async def get_existing_report(
    user: User,
    target_type: str,
    target_id: UUID,
    session: AsyncSession,
) -> Report | None:
    """Get an existing report by reporter + target. Returns None if not found."""
    return await _find_existing_report(
        user.id, target_type, target_id, session
    )


async def update_report(
    report_id: UUID,
    user: User,
    reason: str,
    session: AsyncSession,
) -> Report:
    """Update the reason of a user's own pending report.

    Raises NotFoundError if report not found or user is not the reporter (P-08).
    Raises BadRequestError if report is not pending.
    """
    # M-05 fix: FOR UPDATE prevents race with concurrent admin resolve/dismiss.
    stmt = select(Report).where(Report.id == report_id).with_for_update()
    result = await session.execute(stmt)
    report = result.scalar_one_or_none()

    if not report:
        raise NotFoundError("Report not found")

    # M-04 fix: return 404 (not 403) to avoid leaking resource existence (P-08).
    if report.reporter_id != user.id:
        raise NotFoundError("Report not found")

    if report.status != ReportStatus.PENDING.value:
        raise BadRequestError("Can only edit pending reports")

    report.reason = reason

    logger.info(
        "report_updated",
        report_id=str(report_id),
        reporter_id=str(user.id),
    )

    return report


async def _find_existing_report(
    reporter_id: UUID,
    target_type: str,
    target_id: UUID,
    session: AsyncSession,
) -> Report | None:
    """Find an existing report by reporter + target combination."""
    stmt = select(Report).where(
        Report.reporter_id == reporter_id,
        Report.target_type == target_type,
        Report.target_id == target_id,
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
