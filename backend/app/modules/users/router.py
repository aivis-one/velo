# =============================================================================
# VELO Backend — Users Router
# =============================================================================
#
# ENDPOINTS:
#   GET   /api/v1/users/me  — Get current user profile
#   PATCH /api/v1/users/me  — Update current user profile
# =============================================================================

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.modules.auth.dependencies import get_current_user
from app.modules.users.models import User
from app.modules.users.schemas import UserResponse, UserUpdate
from app.modules.users.service import update_user

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
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> UserResponse:
    """Update the authenticated user's profile.

    Only fields present in the request body are updated.
    User comes from get_current_user (read-only session), so service
    merges it into the write session before updating.
    """
    updated = await update_user(user, body, session)
    return UserResponse.model_validate(updated)
