# =============================================================================
# VELO Backend -- Practice Router (Phase 4.2)
# =============================================================================
#
# ENDPOINTS:
#   POST   /api/v1/practices          -- create (master only)
#   GET    /api/v1/practices/{id}     -- get by id (any auth user)
#   PATCH  /api/v1/practices/{id}     -- update (owner master only)
#   DELETE /api/v1/practices/{id}     -- soft delete draft (owner only)
#
# AUTH:
#   POST/PATCH/DELETE use get_current_master (verified master required).
#   GET uses get_current_user (any authenticated user).
#
# SESSION:
#   Mutating endpoints use get_db_session (write).
#   GET uses get_db_reader (read-only).
# =============================================================================

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_reader, get_db_session
from app.modules.auth.dependencies import get_current_master, get_current_user
from app.modules.masters.models import MasterProfile
from app.modules.practices.schemas import (
    CreatePracticeRequest,
    PracticeResponse,
    UpdatePracticeRequest,
)
from app.modules.practices.service import (
    create_practice,
    delete_practice,
    get_practice,
    update_practice,
)
from app.modules.users.models import User

router = APIRouter(prefix="/api/v1/practices", tags=["practices"])


@router.post(
    "",
    response_model=PracticeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_practice_endpoint(
    body: CreatePracticeRequest,
    master_tuple: tuple[User, MasterProfile] = Depends(
        get_current_master
    ),
    session: AsyncSession = Depends(get_db_session),
) -> PracticeResponse:
    """Create a new practice (verified master only)."""
    user, _profile = master_tuple
    practice = await create_practice(user, body, session)
    await session.flush()
    await session.refresh(practice)
    return PracticeResponse.model_validate(practice)


@router.get("/{practice_id}", response_model=PracticeResponse)
async def get_practice_endpoint(
    practice_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_reader),
) -> PracticeResponse:
    """Get a practice by id.

    Draft/deleted practices are visible only to the owner master.
    """
    practice = await get_practice(practice_id, user, session)
    return PracticeResponse.model_validate(practice)


@router.patch("/{practice_id}", response_model=PracticeResponse)
async def update_practice_endpoint(
    practice_id: UUID,
    body: UpdatePracticeRequest,
    master_tuple: tuple[User, MasterProfile] = Depends(
        get_current_master
    ),
    session: AsyncSession = Depends(get_db_session),
) -> PracticeResponse:
    """Update a practice (owner master only)."""
    user, _profile = master_tuple
    practice = await update_practice(
        practice_id, user, body, session
    )
    await session.flush()
    await session.refresh(practice)
    return PracticeResponse.model_validate(practice)


@router.delete("/{practice_id}", response_model=PracticeResponse)
async def delete_practice_endpoint(
    practice_id: UUID,
    master_tuple: tuple[User, MasterProfile] = Depends(
        get_current_master
    ),
    session: AsyncSession = Depends(get_db_session),
) -> PracticeResponse:
    """Soft-delete a draft practice (owner master only).

    Sets status=deleted. Only works on drafts. Published practices
    must be cancelled via a separate endpoint (Phase 5).
    """
    user, _profile = master_tuple
    practice = await delete_practice(practice_id, user, session)
    await session.flush()
    await session.refresh(practice)
    return PracticeResponse.model_validate(practice)
