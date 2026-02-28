# =============================================================================
# VELO Backend -- Practice Router (Phase 4.2 + 4.3/4.4, updated Phase 6.5,
#                                  updated Frontend F3 prep)
# =============================================================================
#
# ENDPOINTS:
#   GET    /api/v1/practices              -- public feed (4.3)
#   POST   /api/v1/practices              -- create (master only)
#   GET    /api/v1/practices/{id}         -- get by id (any auth user)
#   PATCH  /api/v1/practices/{id}         -- update (owner master only)
#   DELETE /api/v1/practices/{id}         -- soft delete draft (owner only)
#   POST   /api/v1/practices/{id}/cancel  -- cancel + refund all (6.5)
#
# MASTER_NAME (Frontend F3 prep):
#   - list/get endpoints: service returns master_name via JOIN.
#   - create/update/delete/cancel: user object already available from
#     get_current_master dependency, so practice_to_response(p, user.first_name).
#
# AUTH:
#   GET list uses get_current_user (any authenticated user).
#   POST/PATCH/DELETE/CANCEL use get_current_master (verified master).
#   GET by id uses get_current_user (any authenticated user).
#
# SESSION:
#   Read endpoints use get_db_reader.
#   Mutating endpoints use get_db_session (write).
#
# NOTE: GET "" (list) is defined BEFORE GET "/{practice_id}" to avoid
#   FastAPI interpreting query params path as a UUID.
# =============================================================================

from datetime import datetime
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_reader, get_db_session
from app.modules.auth.dependencies import (
    get_current_master,
    get_current_user,
)
from app.modules.masters.models import MasterProfile
from app.modules.practices.schemas import (
    CreatePracticeRequest,
    PaginatedPracticesResponse,
    PracticeResponse,
    UpdatePracticeRequest,
)
from app.modules.practices.service import (
    cancel_practice,
    create_practice,
    delete_practice,
    get_practice,
    list_public_practices,
    practice_to_response,
    update_practice,
)
from app.modules.users.models import User

router = APIRouter(
    prefix="/api/v1/practices", tags=["practices"],
)


# ------------------------------------------------------------------
# GET /api/v1/practices -- public feed (Phase 4.3)
# ------------------------------------------------------------------
@router.get("", response_model=PaginatedPracticesResponse)
async def list_practices_endpoint(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_reader),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    master_id: UUID | None = Query(default=None),
    practice_type: Literal[
        "live", "series", "one_on_one", "replay",
    ] | None = Query(default=None),
    status_filter: Literal[
        "scheduled", "live",
    ] | None = Query(default=None, alias="status"),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    sort_by: Literal[
        "scheduled_at", "price_cents",
    ] = Query(default="scheduled_at"),
    sort_order: Literal["asc", "desc"] = Query(
        default="asc",
    ),
) -> PaginatedPracticesResponse:
    """List practices in the public feed.

    Only scheduled and live practices are shown.
    Supports filters, sorting, and pagination.
    """
    return await list_public_practices(
        session,
        limit=limit,
        offset=offset,
        master_id=master_id,
        practice_type=practice_type,
        status=status_filter,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_order=sort_order,
    )


# ------------------------------------------------------------------
# POST /api/v1/practices -- create (Phase 4.2)
# ------------------------------------------------------------------
@router.post(
    "",
    response_model=PracticeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_practice_endpoint(
    body: CreatePracticeRequest,
    master_tuple: tuple[User, MasterProfile] = Depends(
        get_current_master,
    ),
    session: AsyncSession = Depends(get_db_session),
) -> PracticeResponse:
    """Create a new practice (verified master only)."""
    user, _profile = master_tuple
    practice = await create_practice(user, body, session)
    await session.flush()
    await session.refresh(practice)
    return practice_to_response(practice, user.first_name)


# ------------------------------------------------------------------
# GET /api/v1/practices/{id} -- get by id (Phase 4.2)
# ------------------------------------------------------------------
@router.get(
    "/{practice_id}",
    response_model=PracticeResponse,
)
async def get_practice_endpoint(
    practice_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_reader),
) -> PracticeResponse:
    """Get a practice by id.

    Draft/deleted practices are visible only to the owner master.
    """
    practice, master_name = await get_practice(
        practice_id, user, session,
    )
    return practice_to_response(practice, master_name)


# ------------------------------------------------------------------
# PATCH /api/v1/practices/{id} -- update (Phase 4.2)
# ------------------------------------------------------------------
@router.patch(
    "/{practice_id}",
    response_model=PracticeResponse,
)
async def update_practice_endpoint(
    practice_id: UUID,
    body: UpdatePracticeRequest,
    master_tuple: tuple[User, MasterProfile] = Depends(
        get_current_master,
    ),
    session: AsyncSession = Depends(get_db_session),
) -> PracticeResponse:
    """Update a practice (owner master only)."""
    user, _profile = master_tuple
    practice = await update_practice(
        practice_id, user, body, session,
    )
    await session.flush()
    await session.refresh(practice)
    return practice_to_response(practice, user.first_name)


# ------------------------------------------------------------------
# DELETE /api/v1/practices/{id} -- soft delete (Phase 4.2)
# ------------------------------------------------------------------
@router.delete(
    "/{practice_id}",
    response_model=PracticeResponse,
)
async def delete_practice_endpoint(
    practice_id: UUID,
    master_tuple: tuple[User, MasterProfile] = Depends(
        get_current_master,
    ),
    session: AsyncSession = Depends(get_db_session),
) -> PracticeResponse:
    """Soft-delete a draft practice (owner master only).

    Sets status=deleted. Only works on drafts. Published practices
    must be cancelled via POST /{id}/cancel (Phase 6.5).
    """
    user, _profile = master_tuple
    practice = await delete_practice(practice_id, user, session)
    await session.flush()
    await session.refresh(practice)
    return practice_to_response(practice, user.first_name)


# ------------------------------------------------------------------
# POST /api/v1/practices/{id}/cancel -- cancel + refund (Phase 6.5)
# ------------------------------------------------------------------
@router.post(
    "/{practice_id}/cancel",
    response_model=PracticeResponse,
)
async def cancel_practice_endpoint(
    practice_id: UUID,
    master_tuple: tuple[User, MasterProfile] = Depends(
        get_current_master,
    ),
    session: AsyncSession = Depends(get_db_session),
) -> PracticeResponse:
    """Cancel a practice and refund all participants (owner master only).

    100% refund to every active booking. Waitlist entries cleared.
    Only works on scheduled/live practices. This is the only way
    to transition a practice to cancelled status.
    """
    user, _profile = master_tuple
    practice = await cancel_practice(
        practice_id, user, session,
    )
    await session.flush()
    await session.refresh(practice)
    return practice_to_response(practice, user.first_name)
