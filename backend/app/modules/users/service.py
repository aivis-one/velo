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

    Args:
        user: Current user ORM object (from get_current_user dependency).
        data: Validated update payload.
        session: Read-write database session.

    Returns:
        Updated user ORM object.
    """
    updates = data.model_dump(exclude_unset=True)

    if not updates:
        return user

    for field, value in updates.items():
        setattr(user, field, value)

    # Merge into this session's identity map (user may come from
    # a different session via get_current_user which uses get_db_reader).
    merged_user = await session.merge(user)
    await session.flush()

    logger.info(
        "user_profile_updated",
        user_id=str(merged_user.id),
        fields=list(updates.keys()),
    )

    return merged_user
