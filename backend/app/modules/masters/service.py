# =============================================================================
# VELO Backend — Master Service (updated RACE-06)
# =============================================================================
#
# Business logic for master applications.
#
# APPLY FLOW:
#   1. Check user.role == USER (masters can't reapply)
#   2. Check if MasterProfile exists:
#      a) No profile -> create with status "pending"
#      b) Profile with status "rejected" -> update data, reset to "pending"
#      c) Profile with status "pending" -> ConflictError (already pending)
#      d) Profile with status "verified" -> should not happen (role=master)
#   3. Return updated/created MasterProfile
#
# RACE CONDITION GUARD:
#   Two concurrent apply requests may both pass the SELECT check (no profile).
#   Both try INSERT with the same user_id (PK) -> one gets IntegrityError.
#   We catch IntegrityError after flush() and convert to ConflictError.
#
#   RACE-06: Reapplication path (status=rejected -> pending) now uses
#   SELECT ... FOR UPDATE. Without this, two concurrent reapplications
#   both see status=rejected and both call set_jsonb -- last write wins,
#   potentially losing rejection history from the first write.
#
# JSONB SAFETY:
#   All mutations to MasterProfile.data use set_jsonb() (from JSONBMixin).
#   NEVER assign profile.data = ... directly.
# =============================================================================

from datetime import UTC, datetime
from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, ForbiddenError
from app.modules.masters.models import MasterProfile
from app.modules.masters.schemas import MasterApplyRequest
from app.modules.users.models import User, UserRole

logger = structlog.get_logger()


def _build_data(body: MasterApplyRequest) -> dict:
    """Build JSONB data from application request."""
    return {
        "account": {
            "status": "pending",
            "applied_at": datetime.now(UTC).isoformat(),
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
        "documents": list(body.documents),
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
        old_rejections = [*old_rejections, rejection_record]

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

    # RACE-06: FOR UPDATE prevents two concurrent reapplications from
    # both seeing status=rejected and overwriting each other's set_jsonb.
    # The second request will block until the first commits, then see
    # status=pending -> ConflictError.
    stmt = (
        select(MasterProfile)
        .where(MasterProfile.user_id == user.id)
        .with_for_update()
    )
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing is not None:
        status = existing.data.get("account", {}).get("status")

        if status == "pending":
            raise ConflictError("Application already pending")

        if status == "verified":
            # Should not happen (user.role would be MASTER), but guard anyway.
            raise ConflictError("Already verified as master")

        # Status is "rejected" -- allow reapplication.
        # Uses set_jsonb() to ensure SQLAlchemy detects the JSONB change.
        existing.set_jsonb("data", _build_reapply_data(existing.data, body))
        logger.info(
            "master_reapplication_submitted",
            user_id=str(user.id),
        )
        return existing

    # No existing profile -- create new one.
    # Race condition guard: two concurrent requests may both reach this point.
    # flush() triggers INSERT; if user_id PK already exists, IntegrityError
    # is raised and converted to ConflictError.
    profile = MasterProfile(
        user_id=user.id,
        data=_build_data(body),
    )
    session.add(profile)

    try:
        async with session.begin_nested():
            await session.flush()
    except IntegrityError:
        raise ConflictError("Application already pending")

    logger.info(
        "master_application_submitted",
        user_id=str(user.id),
    )

    return profile


async def get_master_profile(
    user_id: UUID,
    session: AsyncSession,
) -> MasterProfile | None:
    """Fetch MasterProfile by user_id. Returns None if not found."""
    stmt = select(MasterProfile).where(MasterProfile.user_id == user_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
