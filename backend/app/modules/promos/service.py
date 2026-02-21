# =============================================================================
# VELO Backend -- Promo Service (Phase 6.7)
# =============================================================================
#
# Master promo CRUD: create, list, deactivate.
#
# CREATE:
#   1. Validate discount_percent in allowed list.
#   2. Uppercase code, check uniqueness (DB unique constraint + friendly error).
#   3. If practice_id given, verify master owns that practice.
#   4. Create Promo(type="master", master_id=user.id).
#   5. Audit: promo_created.
#
# DEACTIVATE (soft delete):
#   1. Load promo with FOR UPDATE.
#   2. Verify master owns the promo.
#   3. Set is_active=False.
#   4. Audit: promo_deactivated.
#
# SESSION RULES:
#   No session.commit() (P-01). Caller manages transaction.
# =============================================================================

from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import record_audit
from app.core.config import settings
from app.core.exceptions import BadRequestError, NotFoundError
from app.modules.practices.models import Practice
from app.modules.promos.models import Promo, PromoType
from app.modules.promos.schemas import (
    CreateMasterPromoRequest,
    PaginatedPromosResponse,
    PromoResponse,
)
from app.modules.users.models import User

logger = structlog.get_logger()


async def create_master_promo(
    *,
    user: User,
    body: CreateMasterPromoRequest,
    session: AsyncSession,
) -> Promo:
    """Create a master promo code.

    Master promos: the master absorbs the discount from their revenue.

    Args:
        user: Authenticated master user.
        body: Promo creation request.
        session: Active async session.

    Returns:
        The created Promo.

    Raises:
        BadRequestError: Invalid discount, duplicate code, or practice not owned.
    """
    # 1. Validate discount_percent.
    if body.discount_percent not in settings.promo_allowed_discounts:
        raise BadRequestError(
            f"Discount must be one of: {settings.promo_allowed_discounts}"
        )

    # 2. Validate validity window.
    if body.valid_until and body.valid_until <= body.valid_from:
        raise BadRequestError("valid_until must be after valid_from")

    # 3. If practice_id given, verify master owns it.
    if body.practice_id:
        practice = await session.get(Practice, body.practice_id)
        if not practice or practice.master_id != user.id:
            raise BadRequestError(
                "Practice not found or not owned by you"
            )

    # 4. Create promo.
    code_upper = body.code.strip().upper()

    promo = Promo(
        code=code_upper,
        type=PromoType.MASTER.value,
        master_id=user.id,
        practice_id=body.practice_id,
        discount_percent=body.discount_percent,
        max_uses=body.max_uses,
        valid_from=body.valid_from,
        valid_until=body.valid_until,
        first_purchase_only=body.first_purchase_only,
    )

    # SAVEPOINT: catch duplicate code without killing the whole transaction (P-05).
    async with session.begin_nested():
        session.add(promo)
        try:
            await session.flush()
        except IntegrityError:
            raise BadRequestError(
                f"Promo code '{code_upper}' already exists"
            )

    # 5. Audit.
    await record_audit(
        event="promo_created",
        actor_id=user.id,
        actor_type="master",
        target_type="promo",
        target_id=promo.id,
        data={
            "code": code_upper,
            "type": PromoType.MASTER.value,
            "discount_percent": body.discount_percent,
            "practice_id": str(body.practice_id) if body.practice_id else None,
            "max_uses": body.max_uses,
        },
        session=session,
    )

    logger.info(
        "promo_created",
        promo_id=str(promo.id),
        code=code_upper,
        master_id=str(user.id),
        discount_percent=body.discount_percent,
    )

    return promo


async def list_master_promos(
    *,
    user_id: UUID,
    session: AsyncSession,
    limit: int = 20,
    offset: int = 0,
) -> PaginatedPromosResponse:
    """List promos created by the current master (paginated, newest first)."""
    base = select(Promo).where(Promo.master_id == user_id)

    # Total count.
    count_stmt = select(func.count(Promo.id)).where(Promo.master_id == user_id)
    total = (await session.execute(count_stmt)).scalar_one()

    # Paginated items.
    stmt = (
        base
        .order_by(Promo.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(stmt)
    rows = result.scalars().all()

    return PaginatedPromosResponse(
        items=[
            PromoResponse.model_validate(p, from_attributes=True)
            for p in rows
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


async def deactivate_promo(
    *,
    promo_id: UUID,
    user: User,
    session: AsyncSession,
) -> Promo:
    """Soft-delete a master promo (set is_active=False).

    Args:
        promo_id: ID of the promo to deactivate.
        user: Authenticated master user.
        session: Active async session.

    Returns:
        The updated Promo.

    Raises:
        NotFoundError: Promo not found or not owned by this master.
        BadRequestError: Promo already deactivated.
    """
    promo = await session.get(Promo, promo_id, with_for_update=True)

    if not promo or promo.master_id != user.id:
        raise NotFoundError("Promo not found")

    if not promo.is_active:
        raise BadRequestError("Promo is already deactivated")

    promo.is_active = False

    # Audit.
    await record_audit(
        event="promo_deactivated",
        actor_id=user.id,
        actor_type="master",
        target_type="promo",
        target_id=promo.id,
        data={"code": promo.code},
        session=session,
    )

    logger.info(
        "promo_deactivated",
        promo_id=str(promo.id),
        code=promo.code,
        master_id=str(user.id),
    )

    return promo
