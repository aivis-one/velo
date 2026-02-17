# =============================================================================
# VELO Backend -- Admin Users Router (Phase 3.2)
# =============================================================================
#
# ENDPOINTS:
#   GET /api/v1/admin/users                 -- list all users
#   GET /api/v1/admin/masters/list          -- list all masters (with status filter)
#   GET /api/v1/admin/masters/pending       -- shortcut: pending applications
#   GET /api/v1/admin/masters/rejected      -- shortcut: rejected applications
#
# NOTE: masters/list (not just /masters) to avoid path conflict with
#   POST /masters/{user_id}/verify in admin/masters/router.py.
#   FastAPI would confuse "pending" as a user_id UUID otherwise.
#
# AUTH: get_current_admin on every endpoint.
# SESSION: get_db_reader -- all read-only.
# =============================================================================

from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_reader
from app.modules.admin.users.schemas import (
    PaginatedMastersResponse,
    PaginatedUsersResponse,
)
from app.modules.admin.users.service import list_masters, list_users
from app.modules.auth.dependencies import get_current_admin
from app.modules.users.models import User

router = APIRouter()


@router.get("/users", response_model=PaginatedUsersResponse)
async def get_users(
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_reader),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    role: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
) -> PaginatedUsersResponse:
    """List all users with optional filters and pagination."""
    return await list_users(
        session, limit=limit, offset=offset, role=role, is_active=is_active
    )


@router.get("/masters/list", response_model=PaginatedMastersResponse)
async def get_masters(
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_reader),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    # L-04 fix: Literal validates status at FastAPI layer (422 on invalid).
    # Consistent with admin/reports/router.py (P-11).
    status: Literal["pending", "verified", "rejected"] | None = Query(
        default=None,
    ),
) -> PaginatedMastersResponse:
    """List all masters with optional status filter."""
    return await list_masters(
        session, limit=limit, offset=offset, status=status
    )


@router.get("/masters/pending", response_model=PaginatedMastersResponse)
async def get_pending_masters(
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_reader),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> PaginatedMastersResponse:
    """Shortcut: list master applications awaiting verification."""
    return await list_masters(
        session, limit=limit, offset=offset, status="pending"
    )


@router.get("/masters/rejected", response_model=PaginatedMastersResponse)
async def get_rejected_masters(
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_reader),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> PaginatedMastersResponse:
    """Shortcut: list rejected master applications."""
    return await list_masters(
        session, limit=limit, offset=offset, status="rejected"
    )