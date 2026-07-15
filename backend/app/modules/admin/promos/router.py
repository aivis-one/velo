# =============================================================================
# VELO Backend -- Admin Promo Router (Phase 6.7, Batch 3 + T5)
# =============================================================================
#
# ENDPOINTS:
#   POST  /api/v1/admin/promos                  -- create company promo
#   GET   /api/v1/admin/promos                  -- list all promos (admin view)
#   PATCH /api/v1/admin/promos/{id}/deactivate  -- deactivate ANY promo (T5)
#
# AUTH: get_current_admin on every endpoint.
# SESSION: POST/PATCH = get_db_session (write). GET = get_db_reader (read).
# =============================================================================

from typing import Literal
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_reader, get_db_session
from app.modules.admin.promos.schemas import (
    AdminPaginatedPromosResponse,
    CreateCompanyPromoRequest,
)
from app.modules.admin.promos.service import (
    create_company_promo,
    deactivate_promo,
    list_all_promos,
)
from app.modules.auth.dependencies import get_current_admin
from app.modules.promos.schemas import PromoResponse
from app.modules.users.models import User

logger = structlog.get_logger()

router = APIRouter(prefix="/promos")


@router.post(
    "",
    response_model=PromoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_company_promo_endpoint(
    body: CreateCompanyPromoRequest,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session),
) -> PromoResponse:
    """Create a company promo code (platform-wide, marketing budget).

    Company promos: the platform pays for the discount.
    Code is automatically uppercased. Discount must be in the allowed list.
    """
    promo = await create_company_promo(
        admin=admin, body=body, session=session,
    )
    await session.flush()
    await session.refresh(promo)
    return PromoResponse.model_validate(promo, from_attributes=True)


@router.get(
    "",
    response_model=AdminPaginatedPromosResponse,
)
async def list_promos_endpoint(
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_reader),
    # P-11: Literal validates type at FastAPI layer (422 on invalid value).
    type: Literal["company", "master"] | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> AdminPaginatedPromosResponse:
    """List all promos (company + master, admin view).

    Optional filters: type (company|master), is_active (true|false). Each
    master-type item carries the owning master's name (T5).
    """
    return await list_all_promos(
        session,
        type_filter=type,
        is_active_filter=is_active,
        limit=limit,
        offset=offset,
    )


@router.patch(
    "/{promo_id}/deactivate",
    response_model=PromoResponse,
)
async def deactivate_promo_endpoint(
    promo_id: UUID,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session),
) -> PromoResponse:
    """Deactivate ANY promo -- company or master (soft delete, T5).

    Widened 2026-07-15 from company-only (the operator's explicit ask: admin
    must be able to deactivate every master's promos too). A master's own
    PATCH .../promos/{id}/deactivate (ownership-gated) is unaffected.
    """
    promo = await deactivate_promo(
        promo_id=promo_id, admin=admin, session=session,
    )
    await session.flush()
    await session.refresh(promo)
    return PromoResponse.model_validate(promo, from_attributes=True)
