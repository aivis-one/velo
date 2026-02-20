# =============================================================================
# VELO Backend -- Master Router (updated Phase 6.6)
# =============================================================================
#
# Endpoints:
#   POST  /api/v1/masters/apply          -- submit master application
#   GET   /api/v1/masters/me             -- my master profile (Frontend Backlog)
#   PATCH /api/v1/masters/me/payout      -- update payout details (Phase 6.6)
#   GET   /api/v1/masters/me/practices   -- list my practices (Phase 4.2)
# =============================================================================

import copy

import structlog
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_reader, get_db_session
from app.core.exceptions import BadRequestError
from app.modules.auth.dependencies import get_current_master, get_current_user
from app.modules.masters.models import MasterProfile
from app.modules.masters.schemas import (
    MasterApplyRequest,
    MasterApplyResponse,
    MasterProfileResponse,
    PayoutDetailsResponse,
    PayoutDetailsUpdate,
)
from app.modules.masters.service import apply_for_master
from app.modules.practices.schemas import PaginatedPracticesResponse
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


# ===================================================================
# Frontend Backlog: GET /me -- master profile
# ===================================================================


@router.get(
    "/me",
    response_model=MasterProfileResponse,
)
async def get_my_master_profile(
    master_tuple: tuple[User, MasterProfile] = Depends(
        get_current_master,
    ),
    session: AsyncSession = Depends(get_db_reader),
) -> MasterProfileResponse:
    """Return the current master's profile.

    Extracts display fields from the JSONB ``data`` column and
    combines them with cached balance columns (frozen_cents,
    available_cents).  The ``status`` field reflects the master's
    verification status (pending / verified / rejected).
    """
    _user, profile = master_tuple
    data = profile.data
    account = data.get("account", {})
    prof = data.get("profile", {})

    return MasterProfileResponse(
        user_id=profile.user_id,
        status=account.get("status", "pending"),
        display_name=prof.get("display_name"),
        bio=prof.get("bio"),
        methods=prof.get("methods", []),
        experience_years=prof.get("experience_years"),
        frozen_cents=profile.frozen_cents,
        available_cents=profile.available_cents,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


# ===================================================================
# Phase 6.6: PATCH /me/payout -- update payout details
# ===================================================================


@router.patch(
    "/me/payout",
    response_model=PayoutDetailsResponse,
)
async def update_payout_details(
    body: PayoutDetailsUpdate,
    master_tuple: tuple[User, MasterProfile] = Depends(
        get_current_master,
    ),
    session: AsyncSession = Depends(get_db_session),
) -> PayoutDetailsResponse:
    """Update master's payout details (bank, PayPal, etc.).

    Stored in MasterProfile.data.payout. Snapshotted into each
    Withdrawal at creation time (A+C pattern).
    """
    user, _profile = master_tuple

    # Re-load profile in the writer session.
    # get_current_master loads the object in its own session context
    # (reader); we need the profile bound to THIS session for
    # flush() + refresh() to work.
    profile = await session.get(MasterProfile, user.id)
    if not profile:
        raise BadRequestError("Master profile not found")

    payout_data = {
        "method": body.method,
        "details": body.details,
    }

    # P-03: deepcopy + set_jsonb for safe JSONB mutation.
    data = copy.deepcopy(profile.data)
    data["payout"] = payout_data
    profile.set_jsonb("data", data)

    await session.flush()
    await session.refresh(profile)

    logger.info(
        "payout_details_updated",
        user_id=str(profile.user_id),
        method=body.method,
    )

    return PayoutDetailsResponse(**payout_data)


# ===================================================================
# Phase 4.2: GET /me/practices -- my practices
# ===================================================================


# R-04 fix: PaginatedPracticesResponse (with total count),
# consistent with list_public_practices().
@router.get(
    "/me/practices",
    response_model=PaginatedPracticesResponse,
)
async def list_my_practices(
    master_tuple: tuple[User, MasterProfile] = Depends(
        get_current_master
    ),
    session: AsyncSession = Depends(get_db_reader),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> PaginatedPracticesResponse:
    """List practices owned by the current master.

    Excludes deleted practices. Master sees their own drafts.
    Returns paginated response with total count.
    """
    user, _profile = master_tuple
    return await list_master_practices(
        user, session, limit=limit, offset=offset,
    )
