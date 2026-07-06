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

import copy
from datetime import datetime, timezone
from typing import Literal
from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestError, ConflictError, NotFoundError
from app.modules.admin.users.schemas import (
    AdminMasterListItem,
    PaginatedMastersResponse,
    PaginatedUsersResponse,
)
from app.modules.masters.models import MasterProfile
from app.modules.users.models import User, UserRole
from app.modules.users.schemas import UserResponse, credentials_without_admin_home

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


# ---------------------------------------------------------------------------
# Explicit admin make-master (ПРОМТ №292)
# ---------------------------------------------------------------------------
# Distinct from the application-approval path (admin/masters verify_master):
# this is a direct admin grant from the all-users screen, with no prior
# application. It ports scripts/set_role.py `to_master`: create/re-verify a
# MasterProfile and set role=master. Additive JSONB, no migration.

# String stub for master-profile fields left blank on an admin grant; the
# admin can edit them later (mirrors scripts/set_role.py EDIT).
_MAKE_MASTER_EDIT = "Отредактировать"


def _admin_make_master_data(user: User) -> dict:
    """Verified MasterProfile.data for an explicit admin make-master grant.

    Mirrors scripts/set_role.py `_build_verified_data` (which mirrors
    masters/service._build_data) with account.status pre-set to 'verified'.
    Blank profile fields are stubbed; the master/admin edits them later.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    return {
        "account": {
            "status": "verified",
            "applied_at": now_iso,
            "verification": {
                "verified_at": now_iso,
                "verified_by": "admin_make_master",
                "notes": "master granted via admin make-master",
            },
            "rejections": [],
        },
        "profile": {
            "display_name": user.first_name or _MAKE_MASTER_EDIT,
            "email": None,
            "phone": None,
            "bio": _MAKE_MASTER_EDIT,
            "methods": [],
            "experience_years": 0,
            "certifications": [],
        },
        "documents": [],
        "availability": {"is_accepting": True, "note": None},
        "settings": {
            "auto_confirm_bookings": True,
            "max_participants_default": 20,
        },
        "stats": {
            "total_practices": 0,
            "total_participants": 0,
            "avg_rating": None,
        },
        "seed": {"source": "admin_make_master", "granted_at": now_iso},
    }


async def make_master(
    user_id: UUID,
    admin: User,
    session: AsyncSession,
) -> MasterProfile:
    """Explicitly promote a user to master (admin button, ПРОМТ №292).

    Ports scripts/set_role.py `to_master`: if the user has no MasterProfile,
    create a verified one; if a non-verified profile exists, re-verify it in
    place; then set role=master and clear any switched-away-admin marker (R-1,
    credentials_without_admin_home). This is an EXPLICIT admin grant, distinct
    from verify_master (the application-approval path).

    Idempotent-reject: a user who is already a master -> 409 (already_master).
    Write session (get_db_session); the caller flushes (P-01, no commit here).
    """
    user = await session.get(User, user_id)
    if user is None:
        raise NotFoundError("User not found")

    if user.role == UserRole.MASTER:
        raise ConflictError(
            message="User is already a master", code="already_master"
        )

    profile = await session.get(MasterProfile, user_id)
    if profile is None:
        profile = MasterProfile(
            user_id=user_id, data=_admin_make_master_data(user)
        )
        session.add(profile)
    else:
        status = (profile.data or {}).get("account", {}).get("status")
        if status != "verified":
            # Re-verify an existing pending/rejected/suspended profile in place.
            data = copy.deepcopy(profile.data or {})
            acct = data.setdefault("account", {})
            acct["status"] = "verified"
            acct.setdefault(
                "verification",
                {
                    "verified_at": datetime.now(timezone.utc).isoformat(),
                    "verified_by": "admin_make_master",
                    "notes": "re-verified via admin make-master",
                },
            )
            data.setdefault("availability", {})["is_accepting"] = True
            profile.set_jsonb("data", data)

    # Set role=master and clear the switched-away-admin marker (R-1): an
    # authoritative role change makes this the account's home role.
    user.role = UserRole.MASTER.value
    cleared = credentials_without_admin_home(user.credentials)
    if cleared != (user.credentials or {}):
        user.set_jsonb("credentials", cleared)

    logger.info(
        "admin_make_master",
        admin_id=str(admin.id),
        user_id=str(user_id),
    )
    return profile
