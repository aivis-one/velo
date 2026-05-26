# =============================================================================
# VELO Backend -- Diary Router (Phase 8.1-8.4)
# =============================================================================
#
# ENDPOINTS:
#   POST  /api/v1/practices/{id}/checkin    -- upsert check-in
#   GET   /api/v1/users/me/checkins         -- list my check-ins
#   POST  /api/v1/practices/{id}/feedback   -- upsert feedback
#   GET   /api/v1/users/me/feedbacks        -- list my feedbacks
#   POST  /api/v1/diary                     -- create diary entry
#   GET   /api/v1/diary                     -- list my diary entries
#   GET   /api/v1/diary/{id}                -- get single entry
#   PATCH /api/v1/diary/{id}                -- update entry
#   DELETE /api/v1/diary/{id}               -- delete entry
#   GET   /api/v1/practices/{id}/insights   -- master: aggregated insights
#
# CRITICAL-6 fix: removed redundant flush() in upsert endpoints.
#   refresh() only on update path (to fetch server-side updated_at).
#
# AUTH: get_current_user on all endpoints.
# SESSION: write endpoints use get_db_session, read use get_db_reader.
# =============================================================================

from datetime import datetime
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db_reader, get_db_session
from app.modules.auth.dependencies import get_current_user
from app.modules.diary.schemas import (
    CheckinRequest,
    CheckinResponse,
    CreateDiaryEntryRequest,
    DiaryEntryResponse,
    DiaryFeedItem,
    DiaryFeedResponse,
    FeedbackRequest,
    FeedbackResponse,
    PaginatedCheckinsResponse,
    PaginatedDiaryEntriesResponse,
    PaginatedFeedbacksResponse,
    PracticeInsightsResponse,
    UpdateDiaryEntryRequest,
)
from app.modules.diary.service import (
    create_diary_entry,
    delete_diary_entry,
    get_checkin,
    get_diary_entry,
    get_feedback,
    get_practice_insights,
    list_diary_feed,
    list_user_checkins,
    list_user_diary_entries,
    list_user_feedbacks,
    restore_diary_entry,
    update_diary_entry,
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

diary_router = APIRouter(
    prefix="/api/v1/diary", tags=["diary"],
)

# Separate router for the unified feed. Same prefix as diary_router, but it
# MUST be included before diary_router in main.py so the static "/feed" path
# is matched ahead of diary_router's dynamic "/{entry_id}" (otherwise "feed"
# would be parsed as an entry_id UUID and 422).
diary_feed_router = APIRouter(
    prefix="/api/v1/diary", tags=["diary"],
)

practices_insights_router = APIRouter(
    prefix="/api/v1/practices", tags=["diary"],
)


# ===================================================================
# Check-in endpoints (Phase 8.1)
# ===================================================================


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
    """
    checkin, is_new = await upsert_checkin(
        user,
        practice_id,
        mood=body.mood,
        session=session,
        comment=body.comment,
    )
    # CRITICAL-6 fix: refresh only on update to fetch server-side updated_at.
    if not is_new:
        await session.refresh(checkin)

    return CheckinResponse.model_validate(checkin)


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
    """List the current user's check-ins with optional filters."""
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


@checkins_router.get(
    "/checkins/{checkin_id}",
    response_model=CheckinResponse,
)
async def get_checkin_endpoint(
    checkin_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_reader),
) -> CheckinResponse:
    """Get a single check-in owned by the current user (read-only detail)."""
    checkin = await get_checkin(user, checkin_id, session)
    return CheckinResponse.model_validate(checkin)


# ===================================================================
# Feedback endpoints (Phase 8.2)
# ===================================================================


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
    """
    feedback, is_new = await upsert_feedback(
        user,
        practice_id,
        rating=body.rating,
        session=session,
        comment=body.comment,
    )
    # CRITICAL-6 fix: refresh only on update to fetch server-side updated_at.
    if not is_new:
        await session.refresh(feedback)

    return FeedbackResponse.model_validate(feedback)


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
    """List the current user's feedbacks with optional filters."""
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


@feedbacks_router.get(
    "/feedbacks/{feedback_id}",
    response_model=FeedbackResponse,
)
async def get_feedback_endpoint(
    feedback_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_reader),
) -> FeedbackResponse:
    """Get a single feedback owned by the current user (read-only detail)."""
    feedback = await get_feedback(user, feedback_id, session)
    return FeedbackResponse.model_validate(feedback)


# ===================================================================
# Diary entry endpoints (Phase 8.3)
# ===================================================================


@diary_router.post(
    "",
    response_model=DiaryEntryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_diary_entry_endpoint(
    body: CreateDiaryEntryRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> DiaryEntryResponse:
    """Create a new personal diary entry."""
    entry = await create_diary_entry(
        user,
        content=body.content,
        session=session,
        title=body.title,
        mood=body.mood,
        practice_id=body.practice_id,
        entry_type=body.entry_type,
        practice_phase=body.practice_phase,
    )

    return DiaryEntryResponse.model_validate(entry)


@diary_router.get(
    "",
    response_model=PaginatedDiaryEntriesResponse,
)
async def list_my_diary_entries_endpoint(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_reader),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    practice_id: UUID | None = Query(default=None),
    mood: Literal["low", "mid", "high"] | None = Query(default=None),
    entry_type: Literal["note", "dream"] | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
) -> PaginatedDiaryEntriesResponse:
    """List the current user's diary entries with optional filters."""
    items, total = await list_user_diary_entries(
        user,
        session,
        limit=limit,
        offset=offset,
        practice_id=practice_id,
        mood=mood,
        entry_type=entry_type,
        date_from=date_from,
        date_to=date_to,
    )

    return PaginatedDiaryEntriesResponse(
        items=[
            DiaryEntryResponse.model_validate(e) for e in items
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@diary_router.get(
    "/{entry_id}",
    response_model=DiaryEntryResponse,
)
async def get_diary_entry_endpoint(
    entry_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_reader),
) -> DiaryEntryResponse:
    """Get a single diary entry owned by the current user."""
    entry = await get_diary_entry(user, entry_id, session)
    return DiaryEntryResponse.model_validate(entry)


@diary_router.patch(
    "/{entry_id}",
    response_model=DiaryEntryResponse,
)
async def update_diary_entry_endpoint(
    entry_id: UUID,
    body: UpdateDiaryEntryRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> DiaryEntryResponse:
    """Update a diary entry owned by the current user.

    Only provided fields are updated. Use clear_* flags to set
    nullable fields (mood, title, practice_id) to null.
    """
    entry = await update_diary_entry(
        user,
        entry_id,
        session,
        content=body.content,
        title=body.title,
        mood=body.mood,
        practice_id=body.practice_id,
        entry_type=body.entry_type,
        practice_phase=body.practice_phase,
        clear_mood=body.clear_mood,
        clear_title=body.clear_title,
        clear_practice=body.clear_practice,
        clear_practice_phase=body.clear_practice_phase,
    )
    await session.refresh(entry)

    return DiaryEntryResponse.model_validate(entry)


@diary_router.delete(
    "/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_diary_entry_endpoint(
    entry_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    """Delete a diary entry owned by the current user.

    Soft delete -- the entry is hidden (is_deleted=True) and its timeline
    event drops out of the feed, but the row is retained.
    """
    await delete_diary_entry(user, entry_id, session)


@diary_router.post(
    "/{entry_id}/restore",
    response_model=DiaryEntryResponse,
)
async def restore_diary_entry_endpoint(
    entry_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> DiaryEntryResponse:
    """Restore a soft-deleted diary entry owned by the current user.

    Undo for DELETE: clears is_deleted and brings the timeline event back
    into the feed. 404 if the entry is missing, not owned, or not deleted.
    """
    entry = await restore_diary_entry(user, entry_id, session)
    await session.refresh(entry)
    return DiaryEntryResponse.model_validate(entry)


# ===================================================================
# Diary feed endpoint (Diary redesign iteration -- unified timeline)
# ===================================================================


@diary_feed_router.get(
    "/feed",
    response_model=DiaryFeedResponse,
)
async def list_diary_feed_endpoint(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_reader),
    limit: int = Query(
        default=settings.diary_feed_page_size,
        ge=1,
        le=settings.diary_feed_max_page_size,
    ),
    cursor: datetime | None = Query(
        default=None,
        description=(
            "occurred_at of the last item from the previous page; "
            "returns events strictly older than this."
        ),
    ),
    category: list[
        Literal["entries", "dreams", "feedbacks", "checkins", "practices"]
    ]
    | None = Query(
        default=None,
        description=(
            "Filter chips. Omit for all. Repeat the param to union "
            "categories, e.g. ?category=checkins&category=feedbacks."
        ),
    ),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    search: str | None = Query(default=None, min_length=1),
) -> DiaryFeedResponse:
    """List the current user's unified diary timeline (cursor-paginated).

    Aggregates every projected activity (bookings, practice outcomes,
    check-ins, feedbacks, notes) newest-first. Filter chips map to event
    kinds; search is a case-insensitive match over the denormalized text.
    """
    items, next_cursor = await list_diary_feed(
        user,
        session,
        limit=limit,
        cursor=cursor,
        categories=category,
        date_from=date_from,
        date_to=date_to,
        search=search,
    )

    return DiaryFeedResponse(
        items=[DiaryFeedItem.model_validate(e) for e in items],
        next_cursor=next_cursor,
    )


# ===================================================================
# Practice insights endpoint (Phase 8.4, master-facing)
# ===================================================================


@practices_insights_router.get(
    "/{practice_id}/insights",
    response_model=PracticeInsightsResponse,
)
async def get_practice_insights_endpoint(
    practice_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_reader),
) -> PracticeInsightsResponse:
    """Get aggregated anonymous insights for a completed practice.

    Master-only: returns mood distribution, rating distribution,
    participant count, and feedback comments count.
    No individual user data is exposed.
    """
    data = await get_practice_insights(user, practice_id, session)
    return PracticeInsightsResponse(**data)
