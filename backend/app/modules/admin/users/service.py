# =============================================================================
# VELO Backend -- Admin Users Service (Phase 3.2, updated F8-fix)
# =============================================================================
#
# Queries for admin user/master listings.
# All read-only -- use get_db_reader in router.
#
# USERS LIST:
#   Filters: role, is_active
#   Order: created_at DESC (newest first)
#
# MASTERS LIST:
#   Joins User + MasterProfile, filters by JSONB account.status.
#   Shortcuts /pending and /rejected are just status filters.
#
# F8-fix (W-1):
#   get_master_by_id() -- single master lookup by user_id.
#   Used by GET /admin/masters/{user_id} so the frontend review screen
#   can do a proper single-resource fetch instead of scanning 100 items.
# =============================================================================

from typing import Literal
from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestError, NotFoundError
from app.modules.admin.users.schemas import (
    AdminMasterListItem,
    PaginatedMastersResponse,
    PaginatedUsersResponse,
)
from app.modules.masters.models import MasterProfile
from app.modules.users.models import User, UserRole
from app.modules.users.schemas import UserResponse

logger = structlog.get_logger()


async def list_users(
    session: AsyncSession,
    *,
    limit: int = 20,
    offset: int = 0,
    role: str | None = None,
    is_active: bool | None = None,
) -> PaginatedUsersResponse:
    """List all users with optional filters and pagination."""
    # -- Base query --
    query = select(User).order_by(User.created_at.desc())
    count_query = select(func.count(User.id))

    # -- Filters --
    if role is not None:
        try:
            role_enum = UserRole(role)
        except ValueError:
            raise BadRequestError(f"Invalid role: {role}") from None
        query = query.where(User.role == role_enum)
        count_query = count_query.where(User.role == role_enum)

    if is_active is not None:
        query = query.where(User.is_active == is_active)
        count_query = count_query.where(User.is_active == is_active)

    # -- Total count --
    total_result = await session.execute(count_query)
    total = total_result.scalar_one()

    # -- Paginated items --
    query = query.limit(limit).offset(offset)
    result = await session.execute(query)
    users = result.scalars().all()

    return PaginatedUsersResponse(
        items=[UserResponse.model_validate(u) for u in users],
        total=total,
        limit=limit,
        offset=offset,
    )


async def list_masters(
    session: AsyncSession,
    *,
    limit: int = 20,
    offset: int = 0,
    # L-04 fix: type aligned with router Literal (P-11).
    status: Literal["pending", "verified", "rejected"] | None = None,
) -> PaginatedMastersResponse:
    """List masters (users with MasterProfile) with optional status filter.

    Joins User + MasterProfile. Filters by JSONB data.account.status.
    Sequential scan on master_profiles (small table, no GIN index for MVP).
    """
    # -- Base query: join User + MasterProfile --
    query = (
        select(User, MasterProfile)
        .join(MasterProfile, User.id == MasterProfile.user_id)
        .order_by(MasterProfile.created_at.desc())
    )
    count_query = select(func.count(MasterProfile.user_id)).select_from(
        MasterProfile
    )

    # -- Status filter (JSONB) --
    if status is not None:
        jsonb_filter = (
            MasterProfile.data["account"]["status"].as_string() == status
        )
        query = query.where(jsonb_filter)
        count_query = count_query.where(jsonb_filter)

    # -- Total count --
    total_result = await session.execute(count_query)
    total = total_result.scalar_one()

    # -- Paginated items --
    query = query.limit(limit).offset(offset)
    result = await session.execute(query)
    rows = result.all()

    items = [
        AdminMasterListItem(
            id=user.id,
            telegram_id=user.telegram_id,
            first_name=user.first_name,
            last_name=user.last_name,
            avatar_url=user.avatar_url,
            role=str(user.role),
            is_active=user.is_active,
            master_status=profile.data.get("account", {}).get(
                "status", "unknown"
            ),
        )
        for user, profile in rows
    ]

    return PaginatedMastersResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


async def get_master_by_id(
    user_id: UUID,
    session: AsyncSession,
) -> AdminMasterListItem:
    """Fetch a single master by user_id.

    Joins User + MasterProfile. Raises NotFoundError if the user has
    no MasterProfile (i.e. never applied).

    Used by GET /api/v1/admin/masters/{user_id} (F8-fix W-1).
    """
    stmt = (
        select(User, MasterProfile)
        .join(MasterProfile, User.id == MasterProfile.user_id)
        .where(User.id == user_id)
    )
    result = await session.execute(stmt)
    row = result.one_or_none()

    if row is None:
        raise NotFoundError("Master not found")

    user, profile = row
    return AdminMasterListItem(
        id=user.id,
        telegram_id=user.telegram_id,
        first_name=user.first_name,
        last_name=user.last_name,
        avatar_url=user.avatar_url,
        role=str(user.role),
        is_active=user.is_active,
        master_status=profile.data.get("account", {}).get("status", "unknown"),
    )
