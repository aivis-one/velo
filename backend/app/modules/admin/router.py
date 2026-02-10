# =============================================================================
# VELO Backend — Admin Router (Phase 2.3)
# =============================================================================
#
# ⚠️  TEMPORARY MODULE — Phase 3 will restructure this into a full admin
#     module with stats, user lists, and moderation. Do not add endpoints
#     here without planning Phase 3 integration.
#
# ENDPOINTS:
#   POST /api/v1/admin/masters/{user_id}/verify — approve application
#   POST /api/v1/admin/masters/{user_id}/reject — reject application
#
# AUTH: Both endpoints require admin role (get_current_admin).
# =============================================================================

from uuid import UUID

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.modules.admin.schemas import (
    AdminMasterActionResponse,
    RejectMasterRequest,
    VerifyMasterRequest,
)
from app.modules.admin.service import reject_master, verify_master
from app.modules.auth.dependencies import get_current_admin
from app.modules.users.models import User

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.post(
    "/masters/{user_id}/verify",
    response_model=AdminMasterActionResponse,
)
async def verify_master_endpoint(
    user_id: UUID,
    body: VerifyMasterRequest,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session),
) -> AdminMasterActionResponse:
    """Approve a pending master application.

    Sets MasterProfile status to "verified" and upgrades User.role
    to MASTER. Both changes happen in the same transaction.
    """
    profile = await verify_master(user_id, admin, body.notes, session)

    # P-01: flush + refresh, never commit in router.
    await session.flush()
    await session.refresh(profile)

    return AdminMasterActionResponse(
        user_id=profile.user_id,
        status=profile.data["account"]["status"],
    )


@router.post(
    "/masters/{user_id}/reject",
    response_model=AdminMasterActionResponse,
)
async def reject_master_endpoint(
    user_id: UUID,
    body: RejectMasterRequest,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session),
) -> AdminMasterActionResponse:
    """Reject a pending master application.

    Sets MasterProfile status to "rejected" with reason.
    User.role stays as USER — applicant can reapply later.
    """
    profile = await reject_master(user_id, admin, body.reason, session)

    # P-01: flush + refresh, never commit in router.
    await session.flush()
    await session.refresh(profile)

    return AdminMasterActionResponse(
        user_id=profile.user_id,
        status=profile.data["account"]["status"],
    )
