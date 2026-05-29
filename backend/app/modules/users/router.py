# =============================================================================
# VELO Backend — Users Router
# =============================================================================
#
# ENDPOINTS:
#   GET   /api/v1/users/me  — Get current user profile
#   PATCH /api/v1/users/me  — Update current user profile
#
# TD-029 fix: PATCH /users/me now uses get_current_user_write instead of
#   get_current_user. Both the dependency and the router declare
#   Depends(get_db_session), so FastAPI reuses the same session instance
#   for the entire request — one DB connection instead of two.
#   The service no longer needs session.merge().
# =============================================================================

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.modules.auth.dependencies import get_current_user, get_current_user_write
from app.modules.users.models import User
from app.modules.users.schemas import UserResponse, UserUpdate
from app.modules.users.service import reset_user_to_onboarding, update_user

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(
    user: User = Depends(get_current_user),
) -> UserResponse:
    """Return the authenticated user's profile.

    User object is loaded by get_current_user dependency (read-only session).
    No extra DB query needed.
    """
    return UserResponse.model_validate(user)


@router.patch("/me", response_model=UserResponse)
async def update_me(
    body: UserUpdate,
    user: User = Depends(get_current_user_write),
    session: AsyncSession = Depends(get_db_session),
) -> UserResponse:
    """Update the authenticated user's profile.

    TD-029: get_current_user_write and Depends(get_db_session) share
    the same session instance (FastAPI caches Depends within a request).
    The user is already bound to the write session — no merge needed.

    Only fields present in the request body are updated.
    """
    updated = await update_user(user, body, session)
    return UserResponse.model_validate(updated)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    user: User = Depends(get_current_user_write),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    """Delete the authenticated user's account.

    MVP SEMANTICS (see reset_user_to_onboarding): this does NOT erase data or
    deactivate the account. It resets the onboarding flag so the next login
    sends the user through the welcome flow again, with their old data intact.
    The endpoint contract ("DELETE my account") is kept so that real deletion
    can later be implemented by changing only the service body.

    Returns 204 No Content. The frontend then logs the user out (which closes
    the Mini App in Telegram / redirects in standalone).
    """
    await reset_user_to_onboarding(user, session)
