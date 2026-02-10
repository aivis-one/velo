# =============================================================================
# VELO Backend — Master Router
# =============================================================================
#
# Endpoints:
#   POST /api/v1/masters/apply — submit master application (user only)
# =============================================================================

import structlog
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.modules.auth.dependencies import get_current_user
from app.modules.masters.schemas import MasterApplyRequest, MasterApplyResponse
from app.modules.masters.service import apply_for_master
from app.modules.users.models import User

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/masters", tags=["masters"])


@router.post(
    "/apply",
    response_model=MasterApplyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def apply_master(
    body: MasterApplyRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> MasterApplyResponse:
    """Submit a master application.

    Collects profile, experience, and documents from a 3-step form.
    Creates a MasterProfile with status "pending". If a previous
    application was rejected, updates the existing profile.
    """
    profile = await apply_for_master(user, body, session)

    # flush() to get DB-generated defaults (created_at) without
    # explicit commit — get_db_session commits on success after yield.
    await session.flush()
    await session.refresh(profile)

    return MasterApplyResponse(
        user_id=profile.user_id,
        status=profile.data["account"]["status"],
        created_at=profile.created_at,
    )
