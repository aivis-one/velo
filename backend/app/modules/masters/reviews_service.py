# =============================================================================
# VELO Backend -- Master Reviews Service (#3 -- cross-practice attention feed)
# =============================================================================
#
# Owner-scoped, read-only aggregation of named feedbacks across ALL of the
# master's COMPLETED practices -- the cross-practice counterpart to E1's
# per-practice list_practice_reviews.
#
# REUSE (S-2 -- consolidate, do not duplicate): the rating-bucket mapping
# (1-3 confused / 4-7 good / 8-10 fire), the reviewer-name formatter, and the
# attention threshold are imported from diary.service rather than re-copied.
# masters -> diary is a one-way dependency (diary never imports masters), so
# there is no import cycle.
#
# attention=True narrows the feed to the negative (confused) bucket for the
# dashboard "Требуют внимания" block; attention=False returns the full feed.
# Newest-first, paginated. SESSION RULES: read-only, no commit (P-01).
# =============================================================================

from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.diary.models import Feedback
from app.modules.diary.service import (
    _ATTENTION_RATING_MAX,
    _rating_bucket,
    _reviewer_name,
)
from app.modules.practices.models import Practice, PracticeStatus
from app.modules.users.models import User

logger = structlog.get_logger()


async def list_master_reviews(
    master_id: UUID,
    session: AsyncSession,
    *,
    attention: bool = False,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[dict], int]:
    """List named reviews across the master's completed practices.

    Each feedback is joined to its author (name + avatar) and its practice
    (title). Scope is the master's own COMPLETED practices only -- a feedback
    on another master's practice, or on a not-yet-completed one, never appears.
    When attention=True the page is narrowed to the negative bucket
    (rating 1-3) for the dashboard "needs attention" feed.

    Args:
        master_id: The authenticated master's user id (ownership scope).
        session: Read session.
        attention: When True, return only negative reviews (rating 1-3).
        limit: Page size.
        offset: Page offset.

    Returns:
        Tuple of (items, total_count). Each item is a dict ready for
        MasterReviewItem (adds practice_title vs E1's ReviewItem).
    """
    base = (
        select(Feedback, User, Practice.title)
        .join(Practice, Feedback.practice_id == Practice.id)
        .join(User, Feedback.user_id == User.id)
        .where(
            Practice.master_id == master_id,
            Practice.status == PracticeStatus.COMPLETED.value,
        )
    )
    if attention:
        base = base.where(Feedback.rating <= _ATTENTION_RATING_MAX)

    # Total derived from the base query (filters applied once).
    total = (
        await session.execute(
            select(func.count()).select_from(base.subquery())
        )
    ).scalar_one()

    rows = (
        await session.execute(
            base.order_by(Feedback.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
    ).all()

    items = [
        {
            "reviewer_name": _reviewer_name(author),
            "avatar_url": author.avatar_url,
            "rating": _rating_bucket(feedback.rating),
            "comment": feedback.comment,
            "practice_title": practice_title,
            "created_at": feedback.created_at,
        }
        for feedback, author, practice_title in rows
    ]

    return items, total
