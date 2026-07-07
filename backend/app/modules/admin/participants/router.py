# =============================================================================
# VELO Backend -- Admin Participants Router (E1)
# =============================================================================
#
# ENDPOINTS:
#   GET /api/v1/admin/participants -- global participants list (all users)
#
# Feeds the admin «Участников» screen (previously an honest stub with an
# empty list). filter = all | new | active; period = week | month (+ offset
# stepper) scope the new/active windows. Paginated like /admin/users.
#
# AUTH: get_current_admin. SESSION: get_db_reader (read-only).
# =============================================================================

from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_reader
from app.modules.admin.participants.schemas import (
    PaginatedParticipantsResponse,
)
from app.modules.admin.participants.service import list_participants
from app.modules.auth.dependencies import get_current_admin
from app.modules.users.models import User

router = APIRouter()


@router.get("/participants", response_model=PaginatedParticipantsResponse)
async def get_participants(
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_reader),
    filter: Literal["all", "new", "active"] = Query(default="all"),
    period: Literal["week", "month"] = Query(default="week"),
    offset: int = Query(default=0),
    limit: int = Query(default=20, ge=1, le=100),
    page_offset: int = Query(default=0, ge=0),
) -> PaginatedParticipantsResponse:
    """List platform participants (filter new/active over the period window)."""
    return await list_participants(
        session,
        filter=filter,
        period=period,
        offset=offset,
        limit=limit,
        page_offset=page_offset,
    )
