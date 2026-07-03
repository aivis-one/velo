# =============================================================================
# VELO Backend — Auth Dependencies
# =============================================================================
#
# TD-029 fix: added get_current_user_write.
#   PATCH /users/me previously opened two DB sessions:
#     1. get_current_user → get_db_reader (read-only)
#     2. Depends(get_db_session) in the router → write session
#   The service had to call session.merge(user) to transfer the object
#   from the reader to the writer, which is unnecessary overhead.
#
#   get_current_user_write uses get_db_session instead of get_db_reader.
#   FastAPI caches Depends within a request, so if the router also
#   declares Depends(get_db_session), both receive the SAME session
#   instance — one connection total, no merge needed.
#
# DEPENDENCY OVERVIEW:
#   get_current_user       — any authenticated user, read session
#   get_current_user_write — any authenticated user, write session (TD-029)
#   get_optional_user      — optional auth, read session
#   get_current_admin      — admin role required (wraps get_current_user)
#   get_current_master     — verified master required (wraps get_current_user)
# =============================================================================

from uuid import UUID

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_reader, get_db_session
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.modules.auth.service import get_session
from app.modules.masters.models import MasterProfile
from app.modules.users.models import User, UserRole


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _extract_token(request: Request) -> str | None:
    """Extract Bearer token from Authorization header.

    Returns None if header is missing or malformed.
    """
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth[len("Bearer "):]
    return token or None


def _parse_user_id(session_data: dict) -> UUID:
    """Parse user_id from Redis session data.

    Prevents asyncpg DataError (-> 500) if Redis contains corrupted
    or non-UUID values. Returns clean 401 instead.

    Covers: missing key, malformed string, None, non-string types.
    """
    try:
        return UUID(session_data["user_id"])
    except (KeyError, ValueError, TypeError, AttributeError):
        raise UnauthorizedError("Invalid session data") from None


# ---------------------------------------------------------------------------
# Core auth helpers (extracted to avoid duplication between the two variants)
# ---------------------------------------------------------------------------


async def _load_user_from_request(
    request: Request,
    session: AsyncSession,
) -> User:
    """Shared auth logic: token → Redis → DB.

    Raises UnauthorizedError or ForbiddenError on failure.
    Used by both get_current_user and get_current_user_write.
    """
    token = _extract_token(request)
    if not token:
        raise UnauthorizedError("Authorization header required")

    session_data = await get_session(token)
    if not session_data:
        raise UnauthorizedError("Invalid or expired session")

    user_id = _parse_user_id(session_data)
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    # Return 401, not 404 -- valid Redis session but deleted user means
    # the session is effectively stale. 404 would leak that user_id existed.
    if not user:
        raise UnauthorizedError("Invalid or expired session")

    if not user.is_active:
        raise ForbiddenError("Account is deactivated")

    return user


# ---------------------------------------------------------------------------
# Public dependencies
# ---------------------------------------------------------------------------


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_db_reader),
) -> User:
    """Require authenticated user. Returns User or raises 401.

    Loads the user via read-only session (get_db_reader).
    Use for read-only endpoints or as a base for role checks.

    Use as: user: User = Depends(get_current_user)
    """
    return await _load_user_from_request(request, session)


async def get_current_user_write(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> User:
    """Require authenticated user, bound to the write session.

    TD-029: Use on mutating endpoints that need the user object in
    the same write session as their DB writes. FastAPI caches
    Depends(get_db_session) within a request, so declaring
    Depends(get_current_user_write) + Depends(get_db_session) in
    the same endpoint yields ONE shared session — no session.merge()
    needed in the service layer.

    Use as: user: User = Depends(get_current_user_write)
    """
    return await _load_user_from_request(request, session)


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

    user_id = _parse_user_id(session_data)
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


async def get_current_master(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_reader),
) -> tuple[User, MasterProfile]:
    """Require verified master. Returns (User, MasterProfile) or raises 403.

    Checks:
      1. User role is MASTER
      2. MasterProfile exists
      3. MasterProfile status is "verified"

    Use as:
        master_tuple: tuple[User, MasterProfile] = Depends(get_current_master)
        user, profile = master_tuple
    """
    if user.role != UserRole.MASTER:
        raise ForbiddenError("Master access required")

    stmt = select(MasterProfile).where(
        MasterProfile.user_id == user.id
    )
    result = await session.execute(stmt)
    profile = result.scalar_one_or_none()

    # Distinct machine-readable codes (№257): the frontend master-zone entry
    # must tell "no application at all" (-> lead to /master/apply) apart from
    # "application exists but not verified" (-> /master/pending verdict flow).
    # Both stay 403; only the code differs.
    if not profile:
        raise ForbiddenError(
            "Master profile not found",
            code="master_profile_not_found",
        )

    profile_status = profile.data.get("account", {}).get("status")
    if profile_status != "verified":
        raise ForbiddenError(
            "Master profile not verified",
            code="master_profile_not_verified",
        )

    return user, profile
