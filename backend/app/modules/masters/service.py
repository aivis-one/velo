# =============================================================================
# VELO Backend — Master Service
# =============================================================================
#
# Business logic for master applications.
#
# APPLY FLOW:
#   1. Check user.role == USER (masters can't reapply)
#   2. Check if MasterProfile exists:
#      a) No profile → create with status "pending"
#      b) Profile with status "rejected" → update data, reset to "pending"
#      c) Profile with status "pending" → ConflictError (already pending)
#      d) Profile with status "verified" → should not happen (role=master)
#   3. Return updated/created MasterProfile
# =============================================================================

import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, ForbiddenError
from app.modules.masters.models import MasterProfile
from app.modules.masters.schemas import MasterApplyRequest
from app.modules.users.models import User, UserRole

logger = logging.getLogger(__name__)


def _build_data(body: MasterApplyRequest) -> dict:
    """Build JSONB data from application request."""
    return {
        "account": {
            "status": "pending",
            "applied_at": datetime.now(timezone.utc).isoformat(),
            "verification": None,
            "rejections": [],
        },
        "profile": {
            "display_name": body.profile.display_name,
            "email": body.profile.email,
            "phone": body.profile.phone,
            "bio": body.experience.bio,
            "methods": body.experience.methods,
            "experience_years": body.experience.experience_years,
            "certifications": body.experience.certifications,
        },
        "documents": [doc for doc in body.documents],
        "availability": {
            "is_accepting": False,
            "note": None,
        },
        "settings": {
            "auto_confirm_bookings": True,
            "max_participants_default": 20,
        },
        "stats": {
            "total_practices": 0,
            "total_participants": 0,
            "avg_rating": None,
        },
    }


def _build_reapply_data(
    existing_data: dict, body: MasterApplyRequest
) -> dict:
    """Rebuild JSONB data for reapplication, preserving rejection history."""
    new_data = _build_data(body)

    # Carry over rejection history from previous application.
    old_rejections = existing_data.get("account", {}).get("rejections", [])
    old_status = existing_data.get("account", {}).get("status")

    # Archive the previous rejection into history.
    if old_status == "rejected":
        rejection_record = {
            "rejected_at": existing_data.get("account", {}).get(
                "rejected_at"
            ),
            "reason": existing_data.get("account", {}).get(
                "rejection_reason"
            ),
        }
        old_rejections.append(rejection_record)

    new_data["account"]["rejections"] = old_rejections

    return new_data


async def apply_for_master(
    user: User,
    body: MasterApplyRequest,
    session: AsyncSession,
) -> MasterProfile:
    """Submit or resubmit a master application.

    Creates a new MasterProfile or updates an existing rejected one.
    """
    # Only regular users can apply.
    if user.role != UserRole.USER:
        raise ForbiddenError("Only users with role 'user' can apply")

    # Check for existing profile.
    stmt = select(MasterProfile).where(MasterProfile.user_id == user.id)
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing is not None:
        status = existing.data.get("account", {}).get("status")

        if status == "pending":
            raise ConflictError("Application already pending")

        if status == "verified":
            # Should not happen (user.role would be MASTER), but guard anyway.
            raise ConflictError("Already verified as master")

        # Status is "rejected" — allow reapplication.
        existing.data = _build_reapply_data(existing.data, body)
        logger.info(
            "Master reapplication submitted: user_id=%s", user.id
        )
        return existing

    # No existing profile — create new one.
    profile = MasterProfile(
        user_id=user.id,
        data=_build_data(body),
    )
    session.add(profile)
    logger.info("Master application submitted: user_id=%s", user.id)

    return profile


async def get_master_profile(
    user_id: UUID,
    session: AsyncSession,
) -> MasterProfile | None:
    """Fetch MasterProfile by user_id. Returns None if not found."""
    stmt = select(MasterProfile).where(MasterProfile.user_id == user_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
