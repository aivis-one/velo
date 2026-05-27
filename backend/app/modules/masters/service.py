# =============================================================================
# VELO Backend -- Master Service (updated RACE-06)
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
#
# PUBLIC PROFILE (Calendar iteration, S-4):
#   get_public_master_profile() builds the user-facing MasterPublicResponse
#   for GET /masters/{user_id}. Only verified masters are exposed (404
#   otherwise -- we do not reveal pending/rejected applications). The two
#   counters are LIVE ORM aggregates (ORM-only, no raw SQL), NOT read from
#   the stale data.stats JSONB cache.
# =============================================================================

from datetime import UTC, datetime
from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.modules.diary.models import Feedback
from app.modules.masters.models import MasterProfile
from app.modules.masters.schemas import MasterApplyRequest, MasterPublicResponse
from app.modules.practices.models import Practice, PracticeStatus
from app.modules.users.models import User, UserRole

logger = structlog.get_logger()

# Master account status that is publicly visible via GET /masters/{id}.
# Only verified masters are exposed; pending/rejected resolve to 404 so we
# do not reveal the existence of an unverified application.
_PUBLIC_MASTER_STATUS = "verified"

# Practice statuses excluded from the public practices_count aggregate.
# draft and deleted are not "real" practices for a public profile.
_NON_COUNTABLE_PRACTICE_STATUSES = (
    PracticeStatus.DRAFT.value,
    PracticeStatus.DELETED.value,
)


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


async def get_master_display_name(
    master_id: UUID,
    session: AsyncSession,
) -> str:
    """Get master's display name for notification templates.

    NEW-01: Extracted from reminders.py to shared location.
    Used by reminders, waitlist notifications, and any future
    module that needs a human-readable master name.

    Lookup order:
      1. MasterProfile.data.profile.display_name
      2. User.first_name
      3. Fallback: "Master"
    """
    profile = await session.get(MasterProfile, master_id)
    if profile:
        display_name = (
            profile.data.get("profile", {}).get("display_name")
        )
        if display_name:
            return display_name

    user = await session.get(User, master_id)
    if user and user.first_name:
        return user.first_name

    return "Master"


async def is_master_verified(
    master_id: UUID,
    session: AsyncSession,
) -> bool:
    """Whether a master's account status is "verified".

    Used by the diary projections to snapshot the verified badge as-of the
    event (the feed is an append-only historical record). Reads the same
    data.account.status as get_public_master_profile. Returns False when no
    profile exists. Cheap in the projection path: the caller
    (_practice_snapshot) primes the MasterProfile into the session identity
    map first, so this session.get is a cache hit there.
    """
    profile = await session.get(MasterProfile, master_id)
    if profile is None:
        return False
    status = profile.data.get("account", {}).get("status")
    return status == _PUBLIC_MASTER_STATUS


async def get_master_avatar_url(
    master_id: UUID,
    session: AsyncSession,
) -> str | None:
    """Master avatar URL (User.avatar_url, synced from Telegram photo_url).

    Used by the diary projections to snapshot the avatar as-of the event
    (same pattern/rationale as is_master_verified). Returns None when the
    user has no Telegram photo. Cheap in the projection path: the caller
    (_practice_snapshot) primes the User into the session identity map first,
    so this session.get is a cache hit there.
    """
    user = await session.get(User, master_id)
    return user.avatar_url if user else None


async def get_public_master_profile(
    user_id: UUID,
    session: AsyncSession,
) -> MasterPublicResponse:
    """Build the user-facing public master profile (S-4).

    Returns a MasterPublicResponse with display fields, avatar, and two
    live ORM aggregate counters. Only verified masters are exposed.

    Visibility (P-08 style -- do not reveal existence):
      - No MasterProfile row for user_id          -> 404
      - MasterProfile status != "verified"        -> 404

    Counters (ORM-only, never the stale data.stats cache):
      practices_count -- Practice rows for this master, excluding
                         draft/deleted statuses.
      reviews_count   -- Feedback rows across all of this master's
                         practices (joined Feedback -> Practice).

    avatar_url is User.avatar_url (synced from Telegram photo_url on login);
    None when the master has no Telegram photo. The MasterProfile is joined
    via its user_id PK to the users row to read first_name fallback + avatar.
    """
    # Load the profile + owning user in one outer-joined row. MasterProfile
    # PK is user_id (see get_master_display_name), so we match on it.
    stmt = (
        select(MasterProfile, User.first_name, User.avatar_url)
        .join(User, MasterProfile.user_id == User.id)
        .where(MasterProfile.user_id == user_id)
    )
    result = await session.execute(stmt)
    row = result.one_or_none()

    if row is None:
        raise NotFoundError("Master not found")

    profile, first_name, avatar_url = row

    account = profile.data.get("account", {})
    if account.get("status") != _PUBLIC_MASTER_STATUS:
        # Pending/rejected: do not reveal the unverified application.
        raise NotFoundError("Master not found")

    prof = profile.data.get("profile", {})

    # The two counters below run sequentially, not via asyncio.gather:
    # a single AsyncSession does not allow concurrent operations
    # (SQLAlchemy raises "another operation is in progress"), and spinning
    # up a second session/connection just to parallelize two cheap indexed
    # COUNTs on a cold path (profile open) is not worth the overhead.

    # -- Live counter: public practices (excludes draft/deleted) --
    practices_count_stmt = select(func.count(Practice.id)).where(
        Practice.master_id == user_id,
        Practice.status.notin_(_NON_COUNTABLE_PRACTICE_STATUSES),
    )
    practices_count = (
        await session.execute(practices_count_stmt)
    ).scalar_one()

    # -- Live counter: all feedback across this master's practices --
    # Intentionally NOT filtered by Practice.status: this counts every
    # feedback the master ever received (variant A). It is asymmetric with
    # practices_count (which excludes draft/deleted) on purpose -- the two
    # are independent stats on the profile, not a matched pair, so feedback
    # on a since-deleted/cancelled practice still counts as a real review.
    reviews_count_stmt = (
        select(func.count(Feedback.id))
        .join(Practice, Feedback.practice_id == Practice.id)
        .where(Practice.master_id == user_id)
    )
    reviews_count = (
        await session.execute(reviews_count_stmt)
    ).scalar_one()

    # display_name falls back to User.first_name when the profile field is
    # empty (mirrors get_master_display_name lookup order).
    display_name = prof.get("display_name") or first_name

    return MasterPublicResponse(
        user_id=profile.user_id,
        status=account.get("status", _PUBLIC_MASTER_STATUS),
        display_name=display_name,
        bio=prof.get("bio"),
        methods=prof.get("methods", []),
        experience_years=prof.get("experience_years"),
        avatar_url=avatar_url,
        practices_count=practices_count,
        reviews_count=reviews_count,
    )
