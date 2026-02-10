# =============================================================================
# VELO Backend — Admin Service (Phase 2.3)
# =============================================================================
#
# Business logic for admin actions on master applications.
#
# VERIFY FLOW:
#   1. Load MasterProfile by user_id (PK lookup)
#   2. Validate status == "pending"
#   3. Update JSONB: status → "verified", add verification info
#   4. Change User.role → MASTER
#   5. Return updated profile (caller does flush + refresh)
#
# REJECT FLOW:
#   1. Load MasterProfile by user_id
#   2. Validate status == "pending"
#   3. Update JSONB: status → "rejected", store reason
#   4. Do NOT change User.role
#   5. Return updated profile
#
# JSONB SAFETY:
#   All mutations use copy.deepcopy() + set_jsonb() (P-03).
#   NEVER assign profile.data = ... directly.
#
# SESSION RULES:
#   No session.commit() here (P-01). Router calls flush() + refresh().
#   No IntegrityError expected (updating existing rows, not inserting).
# =============================================================================

import copy
from datetime import UTC, datetime
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.modules.masters.models import MasterProfile
from app.modules.users.models import User, UserRole

logger = structlog.get_logger()


async def _load_pending_profile(
    user_id: UUID,
    session: AsyncSession,
) -> MasterProfile:
    """Load MasterProfile and validate it is in 'pending' status.

    Raises NotFoundError if profile doesn't exist.
    Raises ConflictError if profile is not pending.
    """
    profile = await session.get(MasterProfile, user_id)
    if not profile:
        raise NotFoundError("Master application not found")

    status = profile.data.get("account", {}).get("status")
    if status != "pending":
        raise ConflictError(
            f"Application is not pending (current status: {status})"
        )

    return profile


async def verify_master(
    user_id: UUID,
    admin: User,
    notes: str | None,
    session: AsyncSession,
) -> MasterProfile:
    """Verify a pending master application.

    Two things happen:
      1. MasterProfile.data.account.status → "verified" (via set_jsonb)
      2. User.role → MASTER

    Both are in the same transaction — if either fails, nothing changes.
    """
    profile = await _load_pending_profile(user_id, session)

    # -- Update JSONB (P-03: deepcopy + set_jsonb) --
    new_data = copy.deepcopy(profile.data)
    new_data["account"]["status"] = "verified"
    new_data["account"]["verification"] = {
        "verified_at": datetime.now(UTC).isoformat(),
        "verified_by": str(admin.id),
        "notes": notes,
    }
    profile.set_jsonb("data", new_data)

    # -- Upgrade user role --
    user = await session.get(User, user_id)
    if not user:
        # Should never happen (FK constraint), but guard anyway.
        raise NotFoundError("Master application not found")

    user.role = UserRole.MASTER

    logger.info(
        "master_verified",
        user_id=str(user_id),
        admin_id=str(admin.id),
    )

    return profile


async def reject_master(
    user_id: UUID,
    admin: User,
    reason: str,
    session: AsyncSession,
) -> MasterProfile:
    """Reject a pending master application.

    Stores rejection reason and archives it in rejection history.
    Does NOT change User.role — user stays as USER and can reapply.
    """
    profile = await _load_pending_profile(user_id, session)

    # -- Update JSONB (P-03: deepcopy + set_jsonb) --
    new_data = copy.deepcopy(profile.data)
    new_data["account"]["status"] = "rejected"
    new_data["account"]["rejected_at"] = datetime.now(UTC).isoformat()
    new_data["account"]["rejection_reason"] = reason
    new_data["account"]["rejected_by"] = str(admin.id)
    profile.set_jsonb("data", new_data)

    logger.info(
        "master_rejected",
        user_id=str(user_id),
        admin_id=str(admin.id),
        reason=reason,
    )

    return profile
