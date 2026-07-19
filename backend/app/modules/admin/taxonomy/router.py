# =============================================================================
# VELO Backend -- Admin Taxonomy Router (R5, batch R stage 2)
# =============================================================================
#
# ENDPOINTS:
#   GET   /api/v1/admin/taxonomy                              -- full catalog
#   POST  /api/v1/admin/taxonomy/directions                   -- add direction
#   PATCH /api/v1/admin/taxonomy/directions/{direction_id}    -- edit / deactivate
#   POST  /api/v1/admin/taxonomy/directions/{direction_id}/styles -- add style
#   PATCH /api/v1/admin/taxonomy/styles/{style_id}             -- edit / deactivate
#
# AUTH: get_current_admin on every endpoint.
# SESSION: GET = get_db_reader (read). POST/PATCH = get_db_session (write).
# Nothing else consumes these yet -- the FE swap (AdminCatalogView.vue's
# buildCatalog() swap point) is stage 3, not built here.
# =============================================================================

from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_reader, get_db_session
from app.modules.admin.taxonomy.schemas import (
    CreateDirectionRequest,
    CreateStyleRequest,
    TaxonomyDirectionResponse,
    TaxonomyListResponse,
    TaxonomyStyleResponse,
    UpdateTaxonomyItemRequest,
)
from app.modules.admin.taxonomy.service import (
    create_direction,
    create_style,
    list_taxonomy,
    update_direction,
    update_style,
)
from app.modules.auth.dependencies import get_current_admin
from app.modules.users.models import User

logger = structlog.get_logger()

router = APIRouter(prefix="/taxonomy")


@router.get("", response_model=TaxonomyListResponse)
async def list_taxonomy_endpoint(
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_reader),
) -> TaxonomyListResponse:
    """Full direction/style catalog, including inactive rows (admin view)."""
    return await list_taxonomy(session)


@router.post(
    "/directions",
    response_model=TaxonomyDirectionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_direction_endpoint(
    body: CreateDirectionRequest,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session),
) -> TaxonomyDirectionResponse:
    """Add a new direction (source='custom')."""
    direction = await create_direction(body=body, admin=admin, session=session)
    return TaxonomyDirectionResponse.model_validate(direction, from_attributes=True)


@router.patch(
    "/directions/{direction_id}",
    response_model=TaxonomyDirectionResponse,
)
async def update_direction_endpoint(
    direction_id: UUID,
    body: UpdateTaxonomyItemRequest,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session),
) -> TaxonomyDirectionResponse:
    """Partial edit (label / display_order / is_active).

    is_active=false is the deactivate path -- no hard-delete.
    """
    direction = await update_direction(
        direction_id=direction_id, body=body, admin=admin, session=session,
    )
    return TaxonomyDirectionResponse.model_validate(direction, from_attributes=True)


@router.post(
    "/directions/{direction_id}/styles",
    response_model=TaxonomyStyleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_style_endpoint(
    direction_id: UUID,
    body: CreateStyleRequest,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session),
) -> TaxonomyStyleResponse:
    """Add a new style under a direction (source='custom'). 404 if the
    direction doesn't exist."""
    style = await create_style(
        direction_id=direction_id, body=body, admin=admin, session=session,
    )
    return TaxonomyStyleResponse.model_validate(style, from_attributes=True)


@router.patch(
    "/styles/{style_id}",
    response_model=TaxonomyStyleResponse,
)
async def update_style_endpoint(
    style_id: UUID,
    body: UpdateTaxonomyItemRequest,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session),
) -> TaxonomyStyleResponse:
    """Partial edit (label / display_order / is_active).

    is_active=false is the deactivate path -- no hard-delete.
    """
    style = await update_style(
        style_id=style_id, body=body, admin=admin, session=session,
    )
    return TaxonomyStyleResponse.model_validate(style, from_attributes=True)
