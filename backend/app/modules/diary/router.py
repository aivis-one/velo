# =============================================================================
# VELO Backend -- Diary Router (Phase 8.1: Check-ins, Phase 8.2: Feedbacks)
# =============================================================================
#
# ENDPOINTS:
#   POST /api/v1/practices/{id}/checkin    -- create or update check-in
#   GET  /api/v1/users/me/checkins         -- list my check-ins (paginated)
#   POST /api/v1/practices/{id}/feedback   -- create or update feedback
#   GET  /api/v1/users/me/feedbacks        -- list my feedbacks (paginated)
#
# Routers:
#   practices_checkin_router  -- nested under /practices (POST checkin).
#   checkins_router           -- under /users/me (GET list).
#   practices_feedback_router -- nested under /practices (POST feedback).
#   feedbacks_router          -- under /users/me (GET list).
#
# AUTH: get_current_user on all endpoints.
# SESSION: POST uses get_db_session (write). GET uses get_db_reader.
# =============================================================================

from datetime import datetime
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_reader, get_db_session
from app.modules.auth.dependencies import get_current_user
from app.modules.diary.schemas import (
    CheckinRequest,
    CheckinResponse,
    FeedbackRequest,
    FeedbackResponse,
    PaginatedCheckinsResponse,
    PaginatedFeedbacksResponse,
)
from app.modules.diary.service import (
    list_user_checkins,
    list_user_feedbacks,
    upsert_checkin,
    upsert_feedback,
)
from app.modules.users.models import User

practices_checkin_router = APIRouter(
    prefix="/api/v1/practices", tags=["diary"],
)

checkins_router = APIRouter(
    prefix="/api/v1/users/me", tags=["diary"],
)

practices_feedback_router = APIRouter(
    prefix="/api/v1/practices", tags=["diary"],
)

feedbacks_router = APIRouter(
    prefix="/api/v1/users/me", tags=["diary"],
)


# ===================================================================
# Check-in endpoints (Phase 8.1)
# ===================================================================


# ------------------------------------------------------------------
# POST /api/v1/practices/{practice_id}/checkin
# ------------------------------------------------------------------
@practices_checkin_router.post(
    "/{practice_id}/checkin",
    response_model=CheckinResponse,
    status_code=status.HTTP_200_OK,
)
async def upsert_checkin_endpoint(
    practice_id: UUID,
    body: CheckinRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> CheckinResponse:
    """Create or update a pre-practice check-in.

    Returns 200 for both create and update (upsert semantics).
    The check-in window is enforced server-side: opens
    checkin_window_hours before scheduled_at, closes at scheduled_at.
    """
    checkin, _is_new = await upsert_checkin(
        user,
        practice_id,
        mood=body.mood,
        session=session,
        comment=body.comment,
    )
    await session.flush()
    await session.refresh(checkin)

    return CheckinResponse.model_validate(checkin)


# ------------------------------------------------------------------
# GET /api/v1/users/me/checkins
# ------------------------------------------------------------------
@checkins_router.get(
    "/checkins",
    response_model=PaginatedCheckinsResponse,
)
async def list_my_checkins_endpoint(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_reader),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    practice_id: UUID | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
) -> PaginatedCheckinsResponse:
    """List the current user's check-ins with optional filters.

    Filters:
      - practice_id: show check-ins for a specific practice.
      - date_from / date_to: date range on created_at.
    """
    items, total = await list_user_checkins(
        user,
        session,
        limit=limit,
        offset=offset,
        practice_id=practice_id,
        date_from=date_from,
        date_to=date_to,
    )

    return PaginatedCheckinsResponse(
        items=[
            CheckinResponse.model_validate(c) for c in items
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


# ===================================================================
# Feedback endpoints (Phase 8.2)
# ===================================================================


# ------------------------------------------------------------------
# POST /api/v1/practices/{practice_id}/feedback
# ------------------------------------------------------------------
@practices_feedback_router.post(
    "/{practice_id}/feedback",
    response_model=FeedbackResponse,
    status_code=status.HTTP_200_OK,
)
async def upsert_feedback_endpoint(
    practice_id: UUID,
    body: FeedbackRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> FeedbackResponse:
    """Create or update a post-practice feedback.

    Returns 200 for both create and update (upsert semantics).
    Requires attended booking and completed practice.
    Feedback window: up to feedback_window_hours after practice end.
    """
    feedback, _is_new = await upsert_feedback(
        user,
        practice_id,
        rating=body.rating,
        session=session,
        comment=body.comment,
    )
    await session.flush()
    await session.refresh(feedback)

    return FeedbackResponse.model_validate(feedback)


# ------------------------------------------------------------------
# GET /api/v1/users/me/feedbacks
# ------------------------------------------------------------------
@feedbacks_router.get(
    "/feedbacks",
    response_model=PaginatedFeedbacksResponse,
)
async def list_my_feedbacks_endpoint(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_reader),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    practice_id: UUID | None = Query(default=None),
    rating: Literal["fire", "good", "confused"] | None = Query(
        default=None,
    ),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
) -> PaginatedFeedbacksResponse:
    """List the current user's feedbacks with optional filters.

    Filters:
      - practice_id: show feedbacks for a specific practice.
      - rating: filter by rating value (fire/good/confused).
      - date_from / date_to: date range on created_at.
    """
    items, total = await list_user_feedbacks(
        user,
        session,
        limit=limit,
        offset=offset,
        practice_id=practice_id,
        rating=rating,
        date_from=date_from,
        date_to=date_to,
    )

    return PaginatedFeedbacksResponse(
        items=[
            FeedbackResponse.model_validate(f) for f in items
        ],
        total=total,
        limit=limit,
        offset=offset,
    )
