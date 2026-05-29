# =============================================================================
# VELO Backend — Users Service
# =============================================================================
#
# RESPONSIBILITIES:
#   1. Get user by ID
#   2. Update user profile (partial update)
#
# PATTERN:
#   Functions accept AsyncSession and return ORM objects.
#   Router handles HTTP concerns, service handles domain logic.
#
# TD-029 fix: removed session.merge() from update_user.
#   Previously the user came from get_current_user (read-only session),
#   requiring an explicit merge into the write session. Now the router
#   uses get_current_user_write, which loads the user via the same
#   get_db_session instance as the endpoint — merge is unnecessary.
#
# ONBOARDING:
#   onboarding_completed is not a column -- it lives in the credentials
#   JSONB sandbox. update_user routes it there via set_jsonb() (JSONBMixin),
#   which flag_modified()s the column so SQLAlchemy emits the UPDATE.
#   Plain setattr would target a non-existent column and silently no-op.
# =============================================================================

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import User
from app.modules.users.schemas import UserUpdate

logger = structlog.get_logger()

# Fields that are not real columns and must be written into the
# credentials JSONB sandbox instead of via setattr.
#
# onboarding_completed: bool flag (welcome flow).
# phone / bio: profile fields (schema-on-read). They allow an empty string
#   "" as a valid stored value (means "cleared"); None is still dropped
#   below, so clearing is done by sending "", not null. This reuses the
#   exact same write path as onboarding_completed -- no special-casing.
_JSONB_CREDENTIAL_FIELDS = frozenset({"onboarding_completed", "phone", "bio"})


async def update_user(
    user: User,
    data: UserUpdate,
    session: AsyncSession,
) -> User:
    """Apply partial update to user profile.

    Only fields explicitly provided in the request body are updated.
    Uses model_dump(exclude_unset=True) to distinguish between
    "field not sent" and "field sent as null".

    Column fields (first_name, last_name, timezone, language) are applied
    via setattr. JSONB-backed fields (onboarding_completed) are merged into
    the credentials dict via set_jsonb() so the change is tracked.

    The user object must already be bound to the provided session
    (TD-029: ensured by get_current_user_write in the router).

    Args:
        user: Current user ORM object, bound to the write session.
        data: Validated update payload.
        session: Read-write database session (same session that loaded user).

    Returns:
        Updated user ORM object.
    """
    updates = data.model_dump(exclude_unset=True)

    if not updates:
        return user

    # -- Nested notifications object (partial merge) --------------------------
    #
    # notifications is NOT a flat credential field: it is a nested dict, so the
    # plain dict.update() used for flat fields below would REPLACE the whole
    # object and wipe toggles the user did not send. Pull it out first and
    # merge key-by-key onto whatever is stored, preserving untouched flags.
    # model_dump(exclude_unset=True) already dropped keys the client omitted,
    # and None values (no opinion) are skipped here too.
    notifications_update = updates.pop("notifications", None)

    # Split the REMAINING flat JSONB-backed fields from plain column fields.
    #
    # None is dropped for JSONB fields, empty string is kept:
    #   - onboarding_completed: only true/false are meaningful; null would
    #     store {"onboarding_completed": null}, and bool(None) reads back as
    #     False, silently re-triggering onboarding.
    #   - phone / bio: "not sent" and null both mean "leave untouched"; an
    #     empty string "" is a real value meaning "cleared" and IS written.
    # So clearing phone/bio is done by sending "" (not null). This keeps the
    # single shared write path -- "" passes the `is not None` guard, null does
    # not.
    jsonb_updates = {
        field: value
        for field, value in updates.items()
        if field in _JSONB_CREDENTIAL_FIELDS and value is not None
    }
    column_updates = {
        field: value
        for field, value in updates.items()
        if field not in _JSONB_CREDENTIAL_FIELDS
    }

    # Apply plain column fields.
    for field, value in column_updates.items():
        setattr(user, field, value)

    # Apply JSONB-backed fields + the merged notifications object into
    # credentials. We build a NEW dict (copy) and hand it to set_jsonb, which
    # reassigns + flag_modified()s the column. Mutating user.credentials in
    # place would not be detected by SQLAlchemy.
    if jsonb_updates or notifications_update is not None:
        new_credentials = dict(user.credentials or {})

        if jsonb_updates:
            new_credentials.update(jsonb_updates)

        if notifications_update is not None:
            # Merge onto the stored notifications object (or {} if absent),
            # skipping None values (those mean "leave this toggle as is").
            current = new_credentials.get("notifications")
            merged = dict(current) if isinstance(current, dict) else {}
            for key, value in notifications_update.items():
                if value is not None:
                    merged[key] = value
            new_credentials["notifications"] = merged

        user.set_jsonb("credentials", new_credentials)

    await session.flush()

    logger.info(
        "user_profile_updated",
        user_id=str(user.id),
        fields=list(updates.keys()),
    )

    return user


async def reset_user_to_onboarding(
    user: User,
    session: AsyncSession,
) -> User:
    """MVP "delete account": send the user back through onboarding.

    PRODUCT DECISION (MVP): "Удалить аккаунт" does NOT erase data or
    deactivate the account. It only clears the onboarding_completed flag in
    the credentials JSONB. On the next Telegram login the user is treated as
    if new (App.vue shows the welcome/onboarding flow again), while their old
    data (name, phone, bio, bookings) stays in place and resurfaces.

    is_active is intentionally NOT touched: login must still succeed so the
    user lands in onboarding rather than being locked out.

    FUTURE: real deletion / deactivation will change THIS function body only;
    the DELETE /users/me contract stays the same so the frontend does not move.

    Mechanism mirrors update_user's JSONB path: copy credentials, drop the
    flag, set_jsonb() so SQLAlchemy emits the UPDATE.
    """
    new_credentials = dict(user.credentials or {})
    new_credentials["onboarding_completed"] = False
    user.set_jsonb("credentials", new_credentials)

    await session.flush()

    logger.info(
        "user_account_reset_to_onboarding",
        user_id=str(user.id),
    )

    return user
