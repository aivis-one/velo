# =============================================================================
# VELO Backend -- Practice Service (Phase 4.2 + 4.3/4.4, updated Phase 6.5)
# =============================================================================
#
# Business logic for practice CRUD (master-facing) and public listing.
#
# OWNERSHIP:
#   All mutating operations (update, delete, cancel) verify master_id == user.id.
#   Non-owners receive 404 (P-08: do not reveal resource existence).
#   get_practice() applies visibility rules: draft/deleted only for owner.
#
# STATE MACHINE:
#   draft      -> scheduled, deleted
#   scheduled  -> live
#   live       -> completed
#   completed  -> (terminal)
#   cancelled  -> (terminal)
#   deleted    -> (terminal)
#
# IMPORTANT (Phase 6.5):
#   scheduled -> cancelled and live -> cancelled are NO LONGER allowed
#   via PATCH status. The ONLY path to cancelled is through
#   cancel_practice() which handles refunds for all active bookings.
#
# PRICING (Phase 4.3/4.4):
#   is_free=True  -> price_cents forced to 0 (service overrides any value)
#   is_free=False -> price_cents must be > 0 (service raises 400)
#
# CONCURRENCY:
#   update_practice(), delete_practice(), and cancel_practice() use
#   with_for_update() (P-12) to prevent lost updates on status transitions.
#
# DELETE vs CANCEL:
#   DELETE sets status=deleted (only from draft).
#   CANCEL sets status=cancelled + refunds all bookings (Phase 6.5).
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

from app.core.audit import record_audit
from app.core.exceptions import (
    BadRequestError,
    NotFoundError,
)
from app.modules.payments.refund import refund_all_bookings_for_practice
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

# Valid state transitions via PATCH. Terminal states have no outgoing edges.
# Phase 6.5: cancelled is removed from scheduled/live transitions.
# The ONLY way to reach cancelled is via cancel_practice() which
# handles refunds. This prevents accidental PATCH status=cancelled
# that would skip refund logic.
_VALID_TRANSITIONS: dict[str, set[str]] = {
    PracticeStatus.DRAFT.value: {
        PracticeStatus.SCHEDULED.value,
        PracticeStatus.DELETED.value,
    },
    PracticeStatus.SCHEDULED.value: {
        PracticeStatus.LIVE.value,
    },
    PracticeStatus.LIVE.value: {
        PracticeStatus.COMPLETED.value,
    },
}

# Statuses from which cancel_practice() is allowed.
_CANCELLABLE_PRACTICE_STATUSES = {
    PracticeStatus.SCHEDULED.value,
    PracticeStatus.LIVE.value,
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

    Raises NotFoundError if not found or not owner (P-08).
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

    # R-01 fix: 404 not 403 for non-owner (P-08).
    # Consistent with cancel_practice(), bookings, waitlist, reports.
    if practice.master_id != user.id:
        raise NotFoundError("Practice not found")

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
    through cancel_practice() (Phase 6.5) which handles refunds.

    Uses FOR UPDATE to prevent concurrent state changes (P-12).

    Raises NotFoundError if not found or not owner (P-08).
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

    # R-01 fix: 404 not 403 for non-owner (P-08).
    # Consistent with cancel_practice(), bookings, waitlist, reports.
    if practice.master_id != user.id:
        raise NotFoundError("Practice not found")

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


# ===================================================================
# Phase 6.5: Cancel practice (master cancels, refund all bookings)
# ===================================================================


async def cancel_practice(
    practice_id: UUID,
    user: User,
    session: AsyncSession,
) -> Practice:
    """Cancel a scheduled/live practice with full refund to all participants.

    Master-only. This is the ONLY path to Practice.status=cancelled.
    PATCH status=cancelled is intentionally blocked in _VALID_TRANSITIONS.

    Steps:
    1. Lock practice with FOR UPDATE (P-12).
    2. Verify ownership (P-08: 404 not 403).
    3. Verify status is cancellable (scheduled or live).
    4. Refund all active bookings (100% to each user).
    5. Clear waitlist (all active entries -> left).
    6. Set practice status -> cancelled.
    7. Audit log.

    Raises NotFoundError if not found or not owner.
    Raises BadRequestError if practice is not in a cancellable state.
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

    # P-08: 404 not 403 for non-owner.
    if practice.master_id != user.id:
        raise NotFoundError("Practice not found")

    if practice.status not in _CANCELLABLE_PRACTICE_STATUSES:
        raise BadRequestError(
            f"Cannot cancel practice in status "
            f"{practice.status}"
        )

    # Refund all active bookings + clear waitlist.
    refunded_count = await refund_all_bookings_for_practice(
        practice=practice,
        session=session,
    )

    practice.status = PracticeStatus.CANCELLED.value

    # Audit.
    await record_audit(
        event="practice_cancelled_by_master",
        actor_id=user.id,
        actor_type="user",
        target_type="practice",
        target_id=practice.id,
        data={
            "refunded_bookings": refunded_count,
        },
        session=session,
    )

    logger.info(
        "practice_cancelled",
        practice_id=str(practice_id),
        master_id=str(user.id),
        refunded_bookings=refunded_count,
    )

    return practice


async def list_master_practices(
    user: User,
    session: AsyncSession,
    limit: int = 20,
    offset: int = 0,
) -> PaginatedPracticesResponse:
    """List practices owned by the current master.

    R-04 fix: returns PaginatedPracticesResponse (with total count),
    consistent with list_public_practices().

    Excludes deleted practices. Master sees their own drafts.
    """
    base_filter = (
        Practice.master_id == user.id,
        Practice.status != PracticeStatus.DELETED.value,
    )

    # -- Total count --
    count_query = select(func.count(Practice.id)).where(*base_filter)
    total_result = await session.execute(count_query)
    total = total_result.scalar_one()

    # -- Paginated items --
    stmt = (
        select(Practice)
        .where(*base_filter)
        .order_by(Practice.scheduled_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(stmt)
    practices = result.scalars().all()

    return PaginatedPracticesResponse(
        items=[
            PracticeResponse.model_validate(p) for p in practices
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


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
