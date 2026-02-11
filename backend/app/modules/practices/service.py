# =============================================================================
# VELO Backend -- Practice Service (Phase 4.2)
# =============================================================================
#
# Business logic for practice CRUD (master-facing).
#
# OWNERSHIP:
#   All mutating operations (update, delete) verify master_id == user.id.
#   get_practice() applies visibility rules: draft/deleted only for owner.
#
# DELETE vs CANCEL:
#   DELETE sets status=deleted (only from draft).
#   Cancel for published practices will be in Phase 5 (refunds needed).
#
# SESSION RULES:
#   No session.commit() here (P-01). Router handles flush + refresh.
# =============================================================================

from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.modules.practices.models import Practice, PracticeStatus
from app.modules.practices.schemas import (
    CreatePracticeRequest,
    UpdatePracticeRequest,
)
from app.modules.users.models import User

logger = structlog.get_logger()

# Statuses visible to any authenticated user.
_PUBLIC_STATUSES = {
    PracticeStatus.SCHEDULED.value,
    PracticeStatus.LIVE.value,
    PracticeStatus.COMPLETED.value,
    PracticeStatus.CANCELLED.value,
}


async def create_practice(
    user: User,
    body: CreatePracticeRequest,
    session: AsyncSession,
) -> Practice:
    """Create a new practice in draft status."""
    practice = Practice(
        master_id=user.id,
        practice_type=body.practice_type,
        title=body.title,
        description=body.description,
        scheduled_at=body.scheduled_at,
        duration_minutes=body.duration_minutes,
        timezone=body.timezone,
        max_participants=body.max_participants,
        zoom_link=body.zoom_link,
        parent_practice_id=body.parent_practice_id,
    )
    session.add(practice)

    logger.info(
        "practice_created",
        master_id=str(user.id),
        practice_type=body.practice_type,
        title=body.title,
    )

    return practice


async def get_practice(
    practice_id: UUID,
    user: User,
    session: AsyncSession,
) -> Practice:
    """Get a practice by id with visibility rules.

    Draft/deleted practices are visible only to the owner master.
    All other statuses are visible to any authenticated user.
    """
    stmt = select(Practice).where(Practice.id == practice_id)
    result = await session.execute(stmt)
    practice = result.scalar_one_or_none()

    if not practice:
        raise NotFoundError("Practice not found")

    # Draft/deleted visible only to owner (P-08: 404 not 403).
    if (
        practice.status not in _PUBLIC_STATUSES
        and practice.master_id != user.id
    ):
        raise NotFoundError("Practice not found")

    return practice


async def update_practice(
    practice_id: UUID,
    user: User,
    body: UpdatePracticeRequest,
    session: AsyncSession,
) -> Practice:
    """Update a practice. Only the owner master can edit.

    Raises NotFoundError if not found.
    Raises ForbiddenError if not owner (P-06).
    Raises BadRequestError if practice is deleted.
    """
    stmt = select(Practice).where(Practice.id == practice_id)
    result = await session.execute(stmt)
    practice = result.scalar_one_or_none()

    if not practice:
        raise NotFoundError("Practice not found")

    if practice.master_id != user.id:
        raise ForbiddenError("Not the owner of this practice")

    if practice.status == PracticeStatus.DELETED.value:
        raise BadRequestError("Cannot edit a deleted practice")

    # Apply only provided fields.
    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(practice, field, value)

    logger.info(
        "practice_updated",
        practice_id=str(practice_id),
        master_id=str(user.id),
        fields=list(update_data.keys()),
    )

    return practice


async def delete_practice(
    practice_id: UUID,
    user: User,
    session: AsyncSession,
) -> Practice:
    """Soft-delete a draft practice (set status=deleted).

    Only drafts can be deleted. Published practices must be cancelled
    through a separate flow (Phase 5) that handles refunds.

    Raises NotFoundError if not found.
    Raises ForbiddenError if not owner (P-06).
    Raises BadRequestError if not a draft.
    """
    stmt = select(Practice).where(Practice.id == practice_id)
    result = await session.execute(stmt)
    practice = result.scalar_one_or_none()

    if not practice:
        raise NotFoundError("Practice not found")

    if practice.master_id != user.id:
        raise ForbiddenError("Not the owner of this practice")

    if practice.status != PracticeStatus.DRAFT.value:
        raise BadRequestError(
            "Only draft practices can be deleted. "
            "Use cancel for published practices."
        )

    practice.status = PracticeStatus.DELETED.value

    logger.info(
        "practice_deleted",
        practice_id=str(practice_id),
        master_id=str(user.id),
    )

    return practice


async def list_master_practices(
    user: User,
    session: AsyncSession,
    limit: int = 20,
    offset: int = 0,
) -> list[Practice]:
    """List practices owned by the current master.

    Excludes deleted practices. Master sees their own drafts.
    """
    stmt = (
        select(Practice)
        .where(
            Practice.master_id == user.id,
            Practice.status != PracticeStatus.DELETED.value,
        )
        .order_by(Practice.scheduled_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())
