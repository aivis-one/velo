# =============================================================================
# VELO Backend -- Admin Master Service (Phase 2.3, moved Phase 3.1)
# =============================================================================
#
# Business logic for admin actions on master applications.
#
# VERIFY FLOW:
#   1. Load MasterProfile by user_id with FOR UPDATE (P-07)
#   2. Validate status == "pending"
#   3. Update JSONB: status -> "verified", add verification info
#   4. Change User.role -> MASTER
#   5. Record audit event (M-01)
#   6. Return updated profile (caller does flush + refresh)
#
# REJECT FLOW:
#   1. Load MasterProfile by user_id with FOR UPDATE (P-07)
#   2. Validate status == "pending"
#   3. Update JSONB: status -> "rejected", store reason
#   4. Do NOT change User.role
#   5. Record audit event (M-01)
#   6. Return updated profile
#
# JSONB SAFETY:
#   All mutations use copy.deepcopy() + set_jsonb() (P-03).
#   NEVER assign profile.data = ... directly.
#
# SESSION RULES:
#   No session.commit() here (P-01). Router calls flush() + refresh().
# =============================================================================

import copy
import hashlib
import secrets
from datetime import UTC, datetime
from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import record_audit
from app.core.config import settings
from app.core.exceptions import ConflictError, NotFoundError, VeloError
from app.modules.admin.masters.schemas import (
    AdminMethodChangeItem,
    PaginatedMethodChangeRequestsResponse,
)
from app.modules.masters.models import MasterProfile
from app.modules.users.models import User, UserRole

logger = structlog.get_logger()


async def _load_pending_profile(
    user_id: UUID,
    session: AsyncSession,
) -> MasterProfile:
    """Load MasterProfile with FOR UPDATE and validate 'pending' status.

    Uses SELECT FOR UPDATE (P-07) to prevent race condition when two
    admins act on the same application simultaneously.

    Raises NotFoundError if profile doesn't exist.
    Raises ConflictError if profile is not pending.
    """
    stmt = (
        select(MasterProfile)
        .where(MasterProfile.user_id == user_id)
        .with_for_update()
    )
    result = await session.execute(stmt)
    profile = result.scalar_one_or_none()

    if not profile:
        raise NotFoundError("Master application not found")

    status = profile.data.get("account", {}).get("status")
    if status != "pending":
        # P-08: do not leak current status in error message.
        raise ConflictError("Application is not pending")

    return profile


async def verify_master(
    user_id: UUID,
    admin: User,
    notes: str | None,
    session: AsyncSession,
) -> MasterProfile:
    """Verify a pending master application (T4, ПРОМТ №295).

    Sets MasterProfile.data.account.status -> "verified" ONLY. The user's role
    is NOT changed: approval grants master *capability* (a verified profile),
    and the user self-switches into master mode via POST /users/me/role
    (derive_allowed_roles keys on status=="verified"). Keeping role='user'
    lands the approved applicant back in the user zone with the switch offered,
    per the locked call-design.
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

    # M-01: audit trail for master verification.
    await record_audit(
        event="master_verified",
        actor_id=admin.id,
        actor_type="admin",
        target_type="master_profile",
        target_id=user_id,
        data={"notes": notes},
        session=session,
    )

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
    Does NOT change User.role -- user stays as USER and can reapply.
    """
    profile = await _load_pending_profile(user_id, session)

    # -- Update JSONB (P-03: deepcopy + set_jsonb) --
    new_data = copy.deepcopy(profile.data)
    new_data["account"]["status"] = "rejected"
    new_data["account"]["rejected_at"] = datetime.now(UTC).isoformat()
    new_data["account"]["rejection_reason"] = reason
    new_data["account"]["rejected_by"] = str(admin.id)
    profile.set_jsonb("data", new_data)

    # M-01: audit trail for master rejection.
    await record_audit(
        event="master_rejected",
        actor_id=admin.id,
        actor_type="admin",
        target_type="master_profile",
        target_id=user_id,
        data={"reason": reason},
        session=session,
    )

    logger.info(
        "master_rejected",
        user_id=str(user_id),
        admin_id=str(admin.id),
        reason=reason,
    )

    return profile


# ---------------------------------------------------------------------------
# M3 (E19-FLAT): method change-request moderation
# ---------------------------------------------------------------------------


async def _load_profile_with_pending_method_change(
    user_id: UUID,
    session: AsyncSession,
) -> MasterProfile:
    """Load MasterProfile FOR UPDATE and validate a pending method request.

    Mirrors _load_pending_profile but gates on
    data.profile.method_change_request.status == "pending" (P-07 race guard:
    two admins acting on the same request).

    Raises NotFoundError if there is no pending method-change request.
    """
    stmt = (
        select(MasterProfile)
        .where(MasterProfile.user_id == user_id)
        .with_for_update()
    )
    result = await session.execute(stmt)
    profile = result.scalar_one_or_none()

    if not profile:
        raise NotFoundError("Method change request not found")

    request = profile.data.get("profile", {}).get("method_change_request")
    if not isinstance(request, dict) or request.get("status") != "pending":
        raise NotFoundError("Method change request not found")

    return profile


async def list_pending_method_changes(
    session: AsyncSession,
    *,
    limit: int = 20,
    offset: int = 0,
) -> PaginatedMethodChangeRequestsResponse:
    """List masters with a pending method change-request (newest first).

    Joins User + MasterProfile and filters on the JSONB
    data.profile.method_change_request.status == "pending". Read-only.
    """
    pending_filter = (
        MasterProfile.data["profile"]["method_change_request"][
            "status"
        ].as_string()
        == "pending"
    )

    query = (
        select(User, MasterProfile)
        .join(MasterProfile, User.id == MasterProfile.user_id)
        .where(pending_filter)
        .order_by(MasterProfile.created_at.desc())
    )
    count_query = (
        select(func.count(MasterProfile.user_id))
        .select_from(MasterProfile)
        .where(pending_filter)
    )

    total = (await session.execute(count_query)).scalar_one()

    query = query.limit(limit).offset(offset)
    rows = (await session.execute(query)).all()

    items = [
        AdminMethodChangeItem(
            user_id=user.id,
            display_name=profile.data.get("profile", {}).get("display_name"),
            first_name=user.first_name,
            last_name=user.last_name,
            avatar_url=user.avatar_url,
            current_methods=profile.data.get("profile", {}).get("methods", []),
            proposed_methods=profile.data["profile"]["method_change_request"][
                "proposed_methods"
            ],
            submitted_at=profile.data["profile"]["method_change_request"][
                "submitted_at"
            ],
        )
        for user, profile in rows
    ]

    return PaginatedMethodChangeRequestsResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


async def approve_method_change(
    user_id: UUID,
    admin: User,
    session: AsyncSession,
) -> MasterProfile:
    """Approve a pending method change-request.

    Copies proposed_methods into the live data.profile.methods and CLEARS the
    request (so the profile response returns method_change_request=None). No
    User.role change. Caller does flush + refresh.
    """
    profile = await _load_profile_with_pending_method_change(user_id, session)

    new_data = copy.deepcopy(profile.data)
    request = new_data["profile"]["method_change_request"]
    proposed = request.get("proposed_methods", [])

    new_data["profile"]["methods"] = proposed
    # Clear the request -- approval is terminal; the new methods now stand.
    new_data["profile"].pop("method_change_request", None)
    profile.set_jsonb("data", new_data)

    await record_audit(
        event="master_method_change_approved",
        actor_id=admin.id,
        actor_type="admin",
        target_type="master_profile",
        target_id=user_id,
        data={"methods": proposed},
        session=session,
    )

    logger.info(
        "master_method_change_approved",
        user_id=str(user_id),
        admin_id=str(admin.id),
    )

    return profile


async def edit_master_methods(
    user_id: UUID,
    methods: list[str],
    admin: User,
    session: AsyncSession,
) -> MasterProfile:
    """Admin edits a master's methods during review (T3, ПРОМТ №293).

    Overwrites data.profile.methods with the validated flat list. Mirrors
    approve_method_change's JSONB write (deepcopy -> set_jsonb) + audit, but is
    an admin-initiated DIRECT edit — distinct from the master's own
    method-change request (M3). No User.role / status change. Caller does
    flush + refresh.
    """
    profile = await session.get(MasterProfile, user_id)
    if profile is None:
        raise NotFoundError("Master not found")

    new_data = copy.deepcopy(profile.data)
    new_data.setdefault("profile", {})["methods"] = methods
    profile.set_jsonb("data", new_data)

    await record_audit(
        event="master_methods_edited",
        actor_id=admin.id,
        actor_type="admin",
        target_type="master_profile",
        target_id=user_id,
        data={"methods": methods},
        session=session,
    )

    logger.info(
        "master_methods_edited",
        user_id=str(user_id),
        admin_id=str(admin.id),
    )

    return profile


async def reject_method_change(
    user_id: UUID,
    admin: User,
    reason: str,
    session: AsyncSession,
) -> MasterProfile:
    """Reject a pending method change-request.

    Marks the request status "rejected" + stores the reason (the master sees
    it on their profile response); data.profile.methods is unchanged. Caller
    does flush + refresh.
    """
    profile = await _load_profile_with_pending_method_change(user_id, session)

    new_data = copy.deepcopy(profile.data)
    request = new_data["profile"]["method_change_request"]
    request["status"] = "rejected"
    request["decided_at"] = datetime.now(UTC).isoformat()
    request["decided_by"] = str(admin.id)
    request["reject_reason"] = reason
    profile.set_jsonb("data", new_data)

    await record_audit(
        event="master_method_change_rejected",
        actor_id=admin.id,
        actor_type="admin",
        target_type="master_profile",
        target_id=user_id,
        data={"reason": reason},
        session=session,
    )

    logger.info(
        "master_method_change_rejected",
        user_id=str(user_id),
        admin_id=str(admin.id),
    )

    return profile


# ---------------------------------------------------------------------------
# Batch-INVITE (C1=Б): one-time master invite link
# ---------------------------------------------------------------------------


async def issue_master_invite(
    telegram_id: int,
    admin: User,
    session: AsyncSession,
) -> tuple[str, datetime]:
    """Issue a one-time master invite link for an existing User row.

    C1=Б storage: only the token's sha256 lands in the target's
    credentials["master_invite"] (server-written JSONB -- the key is NOT in
    the users PATCH whitelist, so clients can never plant it). The plaintext
    token exists solely inside the returned link. Re-issuing simply
    overwrites the marker, so the previous link stops claiming (TTL=В: no
    expiry, one-time until claimed).

    Raises:
        NotFoundError (invite_target_not_found): no User with this
            telegram_id -- the person must open the bot once first.
        ConflictError (already_master): the target already has role MASTER.
        VeloError 503 (bot_url_not_configured): telegram_bot_url unset.
    """
    stmt = select(User).where(User.telegram_id == telegram_id)
    user = (await session.execute(stmt)).scalar_one_or_none()
    if user is None:
        raise NotFoundError(
            "User with this telegram_id has not opened the bot yet",
            code="invite_target_not_found",
        )
    if user.role == UserRole.MASTER:
        raise ConflictError(
            "User is already a master",
            code="already_master",
        )
    if not settings.telegram_bot_url:
        raise VeloError(
            message="telegram_bot_url is not configured",
            code="bot_url_not_configured",
            status_code=503,
        )

    token = secrets.token_urlsafe(32)
    issued_at = datetime.now(UTC)

    new_credentials = dict(user.credentials or {})
    new_credentials["master_invite"] = {
        "token_sha256": hashlib.sha256(token.encode()).hexdigest(),
        "issued_at": issued_at.isoformat(),
        "issued_by": str(admin.id),
    }
    user.set_jsonb("credentials", new_credentials)

    # M-01: audit trail (the token itself is never logged).
    await record_audit(
        event="master_invite_issued",
        actor_id=admin.id,
        actor_type="admin",
        target_type="user",
        target_id=user.id,
        data={"telegram_id": telegram_id},
        session=session,
    )

    logger.info(
        "master_invite_issued",
        target_user_id=str(user.id),
        telegram_id=telegram_id,
        admin_id=str(admin.id),
    )

    invite_link = (
        f"{settings.telegram_bot_url}?startapp=master_onboarding__{token}"
    )
    return invite_link, issued_at
