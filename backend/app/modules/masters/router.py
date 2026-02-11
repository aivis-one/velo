# =============================================================================
# VELO Backend -- Master Router (updated Phase 4.2)
# =============================================================================
#
# Endpoints:
#   POST /api/v1/masters/apply          -- submit master application
#   GET  /api/v1/masters/me/practices   -- list my practices (Phase 4.2)
# =============================================================================

import structlog
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_reader, get_db_session
from app.modules.auth.dependencies import get_current_master, get_current_user
from app.modules.masters.models import MasterProfile
from app.modules.masters.schemas import MasterApplyRequest, MasterApplyResponse
from app.modules.masters.service import apply_for_master
from app.modules.practices.schemas import PracticeResponse
from app.modules.practices.service import list_master_practices
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
    # explicit commit -- get_db_session commits on success after yield.
    await session.flush()
    await session.refresh(profile)

    return MasterApplyResponse(
        user_id=profile.user_id,
        status=profile.data["account"]["status"],
        created_at=profile.created_at,
    )


@router.get(
    "/me/practices",
    response_model=list[PracticeResponse],
)
async def list_my_practices(
    master_tuple: tuple[User, MasterProfile] = Depends(
        get_current_master
    ),
    session: AsyncSession = Depends(get_db_reader),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[PracticeResponse]:
    """List practices owned by the current master.

    Excludes deleted practices. Master sees their own drafts.
    """
    user, _profile = master_tuple
    practices = await list_master_practices(
        user, session, limit=limit, offset=offset
    )
    return [
        PracticeResponse.model_validate(p) for p in practices
    ]
