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
# =============================================================================

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import User
from app.modules.users.schemas import UserUpdate

logger = structlog.get_logger()


async def update_user(
    user: User,
    data: UserUpdate,
    session: AsyncSession,
) -> User:
    """Apply partial update to user profile.

    Only fields explicitly provided in the request body are updated.
    Uses model_dump(exclude_unset=True) to distinguish between
    "field not sent" and "field sent as null".

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

    for field, value in updates.items():
        setattr(user, field, value)

    await session.flush()

    logger.info(
        "user_profile_updated",
        user_id=str(user.id),
        fields=list(updates.keys()),
    )

    return user
