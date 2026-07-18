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
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from pydantic import AfterValidator
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db_reader, get_db_session
from app.modules.auth.dependencies import (
    get_current_master,
    get_current_user,
)
from app.modules.masters.models import MasterProfile
from app.modules.practices.cancel_service import cancel_practice
from app.modules.practices.listing_service import list_public_practices
from app.modules.practices.schemas import (
    CancelPracticeRequest,
    CreatePracticeRequest,
    PaginatedPracticesResponse,
    PracticeResponse,
    UpdatePracticeRequest,
)
from app.modules.practices.service import (
    create_practice,
    delete_practice,
    get_practice_detail,
    practice_to_response,
    update_practice,
)
from app.modules.users.models import User

router = APIRouter(
    prefix="/api/v1/practices", tags=["practices"],
)


# ------------------------------------------------------------------
# Query-parameter validators (NO-LITERALS policy)
# ------------------------------------------------------------------
# The list-feed endpoint historically hardcoded Literal[...] inline for
# practice_type / direction / difficulty. That duplicated the source of
# truth and went out of sync the moment those lists were extended (422 on
# new values). practice_type / difficulty have no catalog table (out of
# T2's scope) and stay membership-validated below against
# settings.practice_allowed_* -- unchanged.
#
# direction / style are NOT membership-validated here (T2 stage 1 follow-up,
# 2026-07-15). This is a sync AfterValidator on a query param -- it cannot
# query the async DB catalog, the exact wall that moved CREATE/UPDATE
# validation into practices/service.py (_validate_taxonomy()). Teaching this
# validator the same trick (query the catalog on a config miss) would add a
# DB round-trip to every feed request that filters by direction/style, for
# no behavioral gain: a filter is a query, not a security boundary. Passing
# a direction/style that matches no stored practice is not an error -- it is
# correctly an EMPTY result, because list_public_practices() filters with a
# plain `.in_()` against Practice.data["taxonomy"] (JSONB) that naturally
# returns zero rows for a value nothing has. Dropping the check here also
# removes a class of bug permanently: it can never again drift out of sync
# with the create/update union (there is nothing left to keep in sync).
# duration_bucket / time_of_day / status_filter / sort_by / sort_order
# stay as inline Literal -- those are closed, by-design vocabularies that
# are not config-driven.


def _validate_practice_types(v: list[str] | None) -> list[str] | None:
    if not v:
        return v
    allowed = settings.practice_allowed_types
    bad = [x for x in v if x not in allowed]
    if bad:
        raise ValueError(
            f"practice_type must be one of {allowed}, got {bad}"
        )
    return v


def _validate_difficulties(v: list[str] | None) -> list[str] | None:
    if not v:
        return v
    allowed = settings.practice_allowed_difficulties
    bad = [x for x in v if x not in allowed]
    if bad:
        raise ValueError(
            f"difficulty must be one of {allowed}, got {bad}"
        )
    return v


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
    practice_type: Annotated[
        list[str] | None, AfterValidator(_validate_practice_types),
    ] = Query(default=None),
    # direction / style: no membership AfterValidator (T2 follow-up,
    # 2026-07-15) -- see the comment block above. Type/shape only.
    direction: list[str] | None = Query(default=None),
    difficulty: Annotated[
        list[str] | None, AfterValidator(_validate_difficulties),
    ] = Query(default=None),
    style: list[str] | None = Query(default=None),
    duration_bucket: Literal["short", "long"] | None = Query(default=None),
    time_of_day: Literal[
        "night", "morning", "day", "evening",
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

    Default feed shows only upcoming bookable practices (scheduled/live with
    scheduled_at in the future); started and past practices are excluded.
    Passing an explicit ?status= bypasses the future-only gate.
    Supports Calendar filters (direction / difficulty / style /
    duration_bucket / time_of_day), multi-select type/direction/difficulty,
    sorting, and pagination. Per-user is_booked/is_paid flags are included.
    """
    return await list_public_practices(
        session,
        user=user,
        limit=limit,
        offset=offset,
        master_id=master_id,
        practice_type=practice_type,
        direction=direction,
        difficulty=difficulty,
        style=style,
        duration_bucket=duration_bucket,
        time_of_day=time_of_day,
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
    # F1 (№263): this endpoint is owner-only (master guard + ownership check),
    # so the response returns the caller's OWN zoom_link — consistent with the
    # owner-always-sees rule on the detail (M-3) and the master list (Z-6).
    return practice_to_response(practice, user.first_name, zoom_link_visible=True)


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
    return await get_practice_detail(practice_id, user, session)


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
    # F1 (№263): this endpoint is owner-only (master guard + ownership check),
    # so the response returns the caller's OWN zoom_link — consistent with the
    # owner-always-sees rule on the detail (M-3) and the master list (Z-6).
    return practice_to_response(practice, user.first_name, zoom_link_visible=True)


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
    # F1 (№263): this endpoint is owner-only (master guard + ownership check),
    # so the response returns the caller's OWN zoom_link — consistent with the
    # owner-always-sees rule on the detail (M-3) and the master list (Z-6).
    return practice_to_response(practice, user.first_name, zoom_link_visible=True)


# ------------------------------------------------------------------
# POST /api/v1/practices/{id}/cancel -- cancel + refund (Phase 6.5)
# ------------------------------------------------------------------
@router.post(
    "/{practice_id}/cancel",
    response_model=PracticeResponse,
)
async def cancel_practice_endpoint(
    practice_id: UUID,
    body: CancelPracticeRequest | None = None,
    master_tuple: tuple[User, MasterProfile] = Depends(
        get_current_master,
    ),
    session: AsyncSession = Depends(get_db_session),
) -> PracticeResponse:
    """Cancel a practice and refund all participants (owner master only).

    100% refund to every active booking. Waitlist entries cleared. Only works
    on scheduled/live practices. This is the only way to reach cancelled status.

    Optional body {scope}: "this" (the default, or no body) cancels only this
    occurrence; "this_and_future" also cancels every later occurrence of the
    same series (a non-series practice behaves like "this").
    """
    user, _profile = master_tuple
    scope = (body or CancelPracticeRequest()).scope
    practice = await cancel_practice(
        practice_id, user, session, scope=scope,
    )
    await session.flush()
    await session.refresh(practice)
    # F1 (№263): this endpoint is owner-only (master guard + ownership check),
    # so the response returns the caller's OWN zoom_link — consistent with the
    # owner-always-sees rule on the detail (M-3) and the master list (Z-6).
    return practice_to_response(practice, user.first_name, zoom_link_visible=True)
