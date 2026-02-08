# =============================================================================
# VELO Backend — Auth Dependencies
# =============================================================================
#
# FastAPI dependencies for endpoint authorization.
#
# USAGE:
#   @router.get("/users/me")
#   async def get_me(user: User = Depends(get_current_user)):
#       return user
#
#   @router.get("/admin/stats")
#   async def stats(user: User = Depends(get_current_admin)):
#       return ...
#
#   @router.get("/practices")
#   async def list_practices(user: User | None = Depends(get_optional_user)):
#       # user is None for anonymous requests
#       ...
# =============================================================================

import structlog
from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_reader
from app.core.exceptions import ForbiddenError, NotFoundError, UnauthorizedError
from app.modules.auth.service import get_session
from app.modules.users.models import User, UserRole

logger = structlog.get_logger()


def _extract_token(request: Request) -> str | None:
    """Extract Bearer token from Authorization header."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    return None


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_db_reader),
) -> User:
    """Require authenticated user. Returns User or raises 401.

    Use as: user: User = Depends(get_current_user)
    """
    token = _extract_token(request)
    if not token:
        raise UnauthorizedError("Authorization header required")

    session_data = await get_session(token)
    if not session_data:
        raise UnauthorizedError("Invalid or expired session")

    user_id = session_data["user_id"]
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise NotFoundError("User not found")

    if not user.is_active:
        raise ForbiddenError("Account is deactivated")

    return user


async def get_optional_user(
    request: Request,
    session: AsyncSession = Depends(get_db_reader),
) -> User | None:
    """Optional authentication. Returns User or None.

    Use for endpoints that work for both anonymous and logged-in users.
    """
    token = _extract_token(request)
    if not token:
        return None

    session_data = await get_session(token)
    if not session_data:
        return None

    user_id = session_data["user_id"]
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        return None

    return user


async def get_current_admin(
    user: User = Depends(get_current_user),
) -> User:
    """Require admin role. Returns User or raises 403.

    Use as: admin: User = Depends(get_current_admin)
    """
    if user.role != UserRole.ADMIN:
        raise ForbiddenError("Admin access required")
    return user
