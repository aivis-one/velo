# =============================================================================
# VELO Backend -- Admin Promo Service (Phase 6.7, Batch 3 + T5)
# =============================================================================
#
# Admin CRUD for promo codes.
#
# CREATE (company only):
#   1. Validate discount_percent in allowed list.
#   2. Validate validity window (valid_until > valid_from).
#   3. Uppercase code, SAVEPOINT for duplicate check (P-05/BUG-11).
#   4. Create Promo(type="company", master_id=None, practice_id=None).
#   5. Audit: promo_created (actor_type="admin").
#
# LIST ALL:
#   Admin sees ALL promos (company + master). Optional filters:
#   type (company|master), is_active (true|false). Paginated. T5: also joins
#   User for the master's name on master-type rows (company rows -> None),
#   one batched query over the page's master_ids -- no N+1.
#
# DEACTIVATE (T5: company OR master):
#   1. Load promo with FOR UPDATE (P-12).
#   2. Set is_active=False.
#   3. Audit: promo_deactivated (actor_type="admin", carries promo type).
#   Widened from company-only (Batch 3) per the operator's explicit ask
#   (2026-07-14): "админ должен видеть и деактивировать промокоды ВСЕХ
#   мастеров". A master's OWN PATCH (promos/service.py) still exists
#   separately -- that one stays gated on ownership; this is the admin
#   override, unconditional by design.
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
from app.modules.admin.promos.schemas import (
    AdminPaginatedPromosResponse,
    AdminPromoResponse,
    CreateCompanyPromoRequest,
)
from app.modules.promos.models import Promo, PromoType
from app.modules.promos.schemas import PromoResponse
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
) -> AdminPaginatedPromosResponse:
    """List all promos for admin (company + master, paginated).

    T5: joins User for the owning master's name on master-type rows (one
    extra batched query over the page's master_ids -- company rows have
    master_id=None and contribute nothing to that query, no N+1).

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

    # T5: batched master-name lookup for the page (skips the query entirely
    # when the page is all-company / empty).
    master_ids = {p.master_id for p in rows if p.master_id is not None}
    names: dict[UUID, tuple[str | None, str | None]] = {}
    if master_ids:
        name_stmt = select(User.id, User.first_name, User.last_name).where(
            User.id.in_(master_ids)
        )
        for user_id, first_name, last_name in await session.execute(name_stmt):
            names[user_id] = (first_name, last_name)

    return AdminPaginatedPromosResponse(
        items=[
            AdminPromoResponse(
                **PromoResponse.model_validate(p, from_attributes=True).model_dump(),
                master_first_name=names.get(p.master_id, (None, None))[0],
                master_last_name=names.get(p.master_id, (None, None))[1],
            )
            for p in rows
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


async def deactivate_promo(
    *,
    promo_id: UUID,
    admin: User,
    session: AsyncSession,
) -> Promo:
    """Deactivate ANY promo -- company or master (soft delete).

    T5 (2026-07-15): widened from company-only. The operator's explicit ask
    was that admin see AND deactivate every master's promos too -- a master's
    OWN deactivate (promos/service.py, gated on get_current_master +
    ownership) is unaffected and still exists for self-service.

    Args:
        promo_id: Target promo UUID.
        admin: Authenticated admin user.
        session: Active async session.

    Returns:
        The deactivated Promo.

    Raises:
        NotFoundError: Promo not found.
        ConflictError: Promo is already inactive.
    """
    # FOR UPDATE to prevent concurrent deactivation (P-12).
    promo = await session.get(Promo, promo_id, with_for_update=True)

    if not promo:
        raise NotFoundError("Promo not found")

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
        "promo_deactivated_by_admin",
        promo_id=str(promo.id),
        code=promo.code,
        promo_type=promo.type,
        admin_id=str(admin.id),
    )

    return promo
