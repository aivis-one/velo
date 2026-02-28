# =============================================================================
# VELO Backend -- Admin Promo Service (Phase 6.7, Batch 3)
# =============================================================================
#
# Admin CRUD for company promo codes.
#
# CREATE:
#   1. Validate discount_percent in allowed list.
#   2. Validate validity window (valid_until > valid_from).
#   3. Uppercase code, SAVEPOINT for duplicate check (P-05/BUG-11).
#   4. Create Promo(type="company", master_id=None, practice_id=None).
#   5. Audit: promo_created (actor_type="admin").
#
# LIST ALL:
#   Admin sees ALL promos (company + master). Optional filters:
#   type (company|master), is_active (true|false). Paginated.
#
# DEACTIVATE (company only):
#   1. Load promo with FOR UPDATE (P-12).
#   2. Verify type == company (admin cannot deactivate master promos).
#   3. Set is_active=False.
#   4. Audit: promo_deactivated (actor_type="admin").
#
# SESSION RULES:
#   No session.commit() (P-01). Router calls flush + refresh.
# =============================================================================

from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import record_audit
from app.core.config import settings
from app.core.exceptions import BadRequestError, ConflictError, NotFoundError
from app.modules.admin.promos.schemas import CreateCompanyPromoRequest
from app.modules.promos.models import Promo, PromoType
from app.modules.promos.schemas import PaginatedPromosResponse, PromoResponse
from app.modules.users.models import User

logger = structlog.get_logger()


async def create_company_promo(
    *,
    admin: User,
    body: CreateCompanyPromoRequest,
    session: AsyncSession,
) -> Promo:
    """Create a company promo code (platform-wide, marketing budget).

    Args:
        admin: Authenticated admin user.
        body: Promo creation request.
        session: Active async session.

    Returns:
        The created Promo.

    Raises:
        BadRequestError: Invalid discount or duplicate code.
    """
    # 1. Validate discount_percent.
    if body.discount_percent not in settings.promo_allowed_discounts:
        raise BadRequestError(
            f"Discount must be one of: {settings.promo_allowed_discounts}"
        )

    # 2. Validate validity window.
    if body.valid_until and body.valid_until <= body.valid_from:
        raise BadRequestError("valid_until must be after valid_from")

    # 3. Create promo.
    code_upper = body.code.strip().upper()

    promo = Promo(
        code=code_upper,
        type=PromoType.COMPANY.value,
        master_id=None,
        practice_id=None,
        discount_percent=body.discount_percent,
        max_uses=body.max_uses,
        valid_from=body.valid_from,
        valid_until=body.valid_until,
        first_purchase_only=body.first_purchase_only,
    )

    # ERR-05: try/except OUTSIDE begin_nested (P-05).
    # Previously, the except was INSIDE the async with block, which
    # caught IntegrityError before __aexit__ could rollback the
    # savepoint. This left the savepoint in a broken state.
    # Now: begin_nested __aexit__ sees the exception, rolls back the
    # savepoint cleanly, then our except converts it to BadRequestError.
    try:
        async with session.begin_nested():
            session.add(promo)
            await session.flush()
    except IntegrityError:
        raise BadRequestError(
            f"Promo code '{code_upper}' already exists"
        ) from None

    # 4. Audit.
    await record_audit(
        event="promo_created",
        actor_id=admin.id,
        actor_type="admin",
        target_type="promo",
        target_id=promo.id,
        data={
            "code": code_upper,
            "type": PromoType.COMPANY.value,
            "discount_percent": body.discount_percent,
            "max_uses": body.max_uses,
        },
        session=session,
    )

    logger.info(
        "company_promo_created",
        promo_id=str(promo.id),
        code=code_upper,
        admin_id=str(admin.id),
        discount_percent=body.discount_percent,
    )

    return promo


async def list_all_promos(
    session: AsyncSession,
    *,
    type_filter: str | None = None,
    is_active_filter: bool | None = None,
    limit: int = 20,
    offset: int = 0,
) -> PaginatedPromosResponse:
    """List all promos for admin (company + master, paginated).

    Args:
        session: Read-only async session.
        type_filter: Optional filter by promo type (company|master).
        is_active_filter: Optional filter by active status.
        limit: Page size.
        offset: Page offset.

    Returns:
        Paginated list of promos (newest first).
    """
    filters: list = []
    if type_filter:
        filters.append(Promo.type == type_filter)
    if is_active_filter is not None:
        filters.append(Promo.is_active == is_active_filter)

    # Total count.
    count_stmt = select(func.count(Promo.id))
    if filters:
        count_stmt = count_stmt.where(*filters)
    total = (await session.execute(count_stmt)).scalar_one()

    # Paginated items.
    items_stmt = (
        select(Promo)
        .order_by(Promo.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    if filters:
        items_stmt = items_stmt.where(*filters)

    result = await session.execute(items_stmt)
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


async def deactivate_company_promo(
    *,
    promo_id: UUID,
    admin: User,
    session: AsyncSession,
) -> Promo:
    """Deactivate a company promo (soft delete).

    Admin can only deactivate company promos. Master promos are
    managed by their owners via PATCH /masters/me/promos/{id}/deactivate.

    Args:
        promo_id: Target promo UUID.
        admin: Authenticated admin user.
        session: Active async session.

    Returns:
        The deactivated Promo.

    Raises:
        NotFoundError: Promo not found.
        BadRequestError: Promo is not a company promo, or already inactive.
    """
    # FOR UPDATE to prevent concurrent deactivation (P-12).
    promo = await session.get(Promo, promo_id, with_for_update=True)

    if not promo:
        raise NotFoundError("Promo not found")

    if promo.type != PromoType.COMPANY.value:
        raise BadRequestError(
            "Only company promos can be deactivated by admin"
        )

    if not promo.is_active:
        raise ConflictError("Promo is already inactive")

    promo.is_active = False

    # Audit.
    await record_audit(
        event="promo_deactivated",
        actor_id=admin.id,
        actor_type="admin",
        target_type="promo",
        target_id=promo.id,
        data={
            "code": promo.code,
            "type": promo.type,
        },
        session=session,
    )

    logger.info(
        "company_promo_deactivated",
        promo_id=str(promo.id),
        code=promo.code,
        admin_id=str(admin.id),
    )

    return promo
