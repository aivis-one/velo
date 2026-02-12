# =============================================================================
# VELO Backend -- Practice Service (Phase 4.2 + 4.3/4.4)
# =============================================================================
#
# Business logic for practice CRUD (master-facing) and public listing.
#
# OWNERSHIP:
#   All mutating operations (update, delete) verify master_id == user.id.
#   get_practice() applies visibility rules: draft/deleted only for owner.
#
# STATE MACHINE:
#   draft      -> scheduled, deleted
#   scheduled  -> live, cancelled
#   live       -> completed, cancelled
#   completed  -> (terminal)
#   cancelled  -> (terminal)
#   deleted    -> (terminal)
#
# PRICING (Phase 4.3/4.4):
#   is_free=True  -> price_cents forced to 0 (service overrides any value)
#   is_free=False -> price_cents must be > 0 (service raises 400)
#
# CONCURRENCY:
#   update_practice() and delete_practice() use with_for_update() (P-12)
#   to prevent lost updates on status transitions.
#
# DELETE vs CANCEL:
#   DELETE sets status=deleted (only from draft).
#   Cancel for published practices will be in Phase 5 (refunds needed).
#
# SESSION RULES:
#   No session.commit() here (P-01). Router handles flush + refresh.
# =============================================================================

from datetime import datetime
from typing import Literal
from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    BadRequestError,
    ForbiddenError,
    NotFoundError,
)
from app.modules.practices.models import Practice, PracticeStatus
from app.modules.practices.schemas import (
    CreatePracticeRequest,
    PaginatedPracticesResponse,
    PracticeResponse,
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

# Statuses shown in public feed (4.3).
_FEED_STATUSES = {
    PracticeStatus.SCHEDULED.value,
    PracticeStatus.LIVE.value,
}

# Valid state transitions. Terminal states have no outgoing edges.
_VALID_TRANSITIONS: dict[str, set[str]] = {
    PracticeStatus.DRAFT.value: {
        PracticeStatus.SCHEDULED.value,
        PracticeStatus.DELETED.value,
    },
    PracticeStatus.SCHEDULED.value: {
        PracticeStatus.LIVE.value,
        PracticeStatus.CANCELLED.value,
    },
    PracticeStatus.LIVE.value: {
        PracticeStatus.COMPLETED.value,
        PracticeStatus.CANCELLED.value,
    },
}

# NOT NULL columns that cannot be set to None via PATCH (P-02).
_NOT_NULL_FIELDS = {
    "title",
    "scheduled_at",
    "duration_minutes",
    "timezone",
    "is_free",
    "price_cents",
    "currency",
}


def _enforce_pricing(
    is_free: bool,
    price_cents: int,
) -> int:
    """Enforce pricing invariant.

    is_free=True  -> return 0 (override any client value).
    is_free=False -> price_cents must be > 0, else raise 400.
    """
    if is_free:
        return 0
    if price_cents <= 0:
        raise BadRequestError(
            "price_cents must be > 0 for paid practices"
        )
    return price_cents


async def create_practice(
    user: User,
    body: CreatePracticeRequest,
    session: AsyncSession,
) -> Practice:
    """Create a new practice in draft status."""
    price_cents = _enforce_pricing(body.is_free, body.price_cents)

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
        is_free=body.is_free,
        price_cents=price_cents,
        currency=body.currency,
    )
    session.add(practice)

    logger.info(
        "practice_created",
        master_id=str(user.id),
        practice_type=body.practice_type,
        title=body.title,
        is_free=body.is_free,
        price_cents=price_cents,
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

    Uses FOR UPDATE to prevent lost updates on concurrent
    status transitions (P-12).

    Raises NotFoundError if not found.
    Raises ForbiddenError if not owner (P-06).
    Raises BadRequestError if practice is deleted/terminal,
        if NOT NULL field set to null (P-02),
        if status transition is invalid,
        or if pricing invariant is violated.
    """
    stmt = (
        select(Practice)
        .where(Practice.id == practice_id)
        .with_for_update()
    )
    result = await session.execute(stmt)
    practice = result.scalar_one_or_none()

    if not practice:
        raise NotFoundError("Practice not found")

    if practice.master_id != user.id:
        raise ForbiddenError("Not the owner of this practice")

    if practice.status == PracticeStatus.DELETED.value:
        raise BadRequestError("Cannot edit a deleted practice")

    update_data = body.model_dump(exclude_unset=True)

    # Guard NOT NULL fields against explicit null (P-02).
    for field in _NOT_NULL_FIELDS:
        if field in update_data and update_data[field] is None:
            raise BadRequestError(f"{field} cannot be null")

    # Validate status transition if status is being changed.
    if "status" in update_data:
        new_status = update_data["status"]
        allowed = _VALID_TRANSITIONS.get(practice.status, set())
        if new_status not in allowed:
            raise BadRequestError(
                f"Cannot transition from "
                f"{practice.status} to {new_status}"
            )

    # Enforce pricing invariant after applying updates.
    # Resolve final is_free and price_cents from mix of
    # existing values and incoming updates.
    final_is_free = update_data.get("is_free", practice.is_free)
    final_price = update_data.get(
        "price_cents", practice.price_cents,
    )
    if "is_free" in update_data or "price_cents" in update_data:
        final_price = _enforce_pricing(final_is_free, final_price)
        update_data["price_cents"] = final_price

    # Apply only provided fields.
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

    Uses FOR UPDATE to prevent concurrent state changes (P-12).

    Raises NotFoundError if not found.
    Raises ForbiddenError if not owner (P-06).
    Raises BadRequestError if not a draft.
    """
    stmt = (
        select(Practice)
        .where(Practice.id == practice_id)
        .with_for_update()
    )
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


async def list_public_practices(
    session: AsyncSession,
    *,
    limit: int = 20,
    offset: int = 0,
    master_id: UUID | None = None,
    practice_type: str | None = None,
    status: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    sort_by: Literal[
        "scheduled_at", "price_cents",
    ] = "scheduled_at",
    sort_order: Literal["asc", "desc"] = "asc",
) -> PaginatedPracticesResponse:
    """List practices visible in the public feed.

    Only scheduled and live practices are shown (unless
    status filter explicitly requests one of them).
    Supports filtering by master, type, date range, and status.
    Supports sorting by scheduled_at or price_cents.
    """
    # -- Base query: only feed-visible statuses --
    base_filter = Practice.status.in_(_FEED_STATUSES)

    # Override with explicit status filter (must still be in
    # feed statuses -- Literal in router guarantees this).
    if status is not None:
        base_filter = Practice.status == status

    query = select(Practice).where(base_filter)
    count_query = select(func.count(Practice.id)).where(
        base_filter,
    )

    # -- Optional filters --
    if master_id is not None:
        query = query.where(Practice.master_id == master_id)
        count_query = count_query.where(
            Practice.master_id == master_id,
        )

    if practice_type is not None:
        query = query.where(
            Practice.practice_type == practice_type,
        )
        count_query = count_query.where(
            Practice.practice_type == practice_type,
        )

    if date_from is not None:
        query = query.where(Practice.scheduled_at >= date_from)
        count_query = count_query.where(
            Practice.scheduled_at >= date_from,
        )

    if date_to is not None:
        query = query.where(Practice.scheduled_at <= date_to)
        count_query = count_query.where(
            Practice.scheduled_at <= date_to,
        )

    # -- Sort --
    sort_column = (
        Practice.price_cents
        if sort_by == "price_cents"
        else Practice.scheduled_at
    )
    if sort_order == "desc":
        sort_column = sort_column.desc()
    else:
        sort_column = sort_column.asc()
    query = query.order_by(sort_column)

    # -- Total count --
    total_result = await session.execute(count_query)
    total = total_result.scalar_one()

    # -- Paginated items --
    query = query.limit(limit).offset(offset)
    result = await session.execute(query)
    practices = result.scalars().all()

    return PaginatedPracticesResponse(
        items=[
            PracticeResponse.model_validate(p) for p in practices
        ],
        total=total,
        limit=limit,
        offset=offset,
    )
