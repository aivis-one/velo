# =============================================================================
# VELO Backend — Auth Router (updated W-06: logout-all, FIX 2.3,
#                              CRITICAL-4: rate limiting, WARNING-4: anti-replay)
# =============================================================================
#
# ENDPOINTS:
#   POST /api/v1/auth/telegram     — Login via Telegram WebApp initData
#   POST /api/v1/auth/logout       — Logout current session
#   POST /api/v1/auth/logout-all   — Logout all sessions (W-06)
#
# CRITICAL-4: Rate limiting on POST /auth/telegram.
#   Max 5 requests per 60 seconds per telegram_id.
#   Prevents Redis OOM via session flooding from a replayed valid initData.
#
# WARNING-4: Anti-replay protection for initData.
#   Each initData hash is stored in Redis with TTL=300s (5-minute window).
#   A second request with the same initData within the window is rejected.
# =============================================================================

import structlog
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db_session
from app.core.exceptions import BadRequestError
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.schemas import AuthResponse, TelegramAuthRequest
from app.modules.auth.service import (
    TelegramValidationError,
    check_auth_rate_limit,
    check_init_data_replay,
    create_session,
    delete_all_sessions,
    delete_session,
    upsert_user_on_login,
    validate_telegram_init_data,
)
from app.modules.users.models import User

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/telegram", response_model=AuthResponse)
async def auth_telegram(
    body: TelegramAuthRequest,
    session: AsyncSession = Depends(get_db_session),
) -> AuthResponse:
    """Authenticate via Telegram WebApp.

    Flow:
      1. Validate initData signature (HMAC-SHA256)
      2. WARNING-4: Reject replayed initData (Redis SET NX, TTL 5 min)
      3. CRITICAL-4: Rate limit per telegram_id (5 req / 60s)
      4. Find or create User by telegram_id
      5. Flush DB (get user.id) -- commit deferred to get_db_session
      6. Create session in Redis (token, TTL 30 days)
      7. Return user + session_token
    """
    # Step 1: Validate initData from Telegram.
    try:
        telegram_user = validate_telegram_init_data(
            body.init_data,
            settings.telegram_bot_token,
        )
    except TelegramValidationError as e:
        logger.warning("telegram_auth_failed", reason=str(e))
        raise BadRequestError(str(e)) from e

    # Step 2: WARNING-4 -- Anti-replay: each initData can only be used once
    # within its 5-minute validity window.
    try:
        await check_init_data_replay(body.init_data)
    except TelegramValidationError as e:
        logger.warning("telegram_auth_replay", reason=str(e))
        raise BadRequestError(str(e)) from e

    # Step 3: CRITICAL-4 -- Rate limit per telegram_id.
    try:
        await check_auth_rate_limit(telegram_user["id"])
    except TelegramValidationError as e:
        logger.warning(
            "telegram_auth_rate_limited",
            telegram_id=telegram_user["id"],
        )
        raise BadRequestError(str(e)) from e

    # Step 4: Create or update user.
    user = await upsert_user_on_login(telegram_user, session)

    # Step 5: M-02 fix: flush (not commit) to get user.id for Redis.
    # get_db_session will commit after return. If Redis fails,
    # the entire transaction rolls back -- no orphan DB records.
    await session.flush()

    # Step 6: Create session in Redis.
    token = await create_session(user)

    return AuthResponse(
        user=user,  # type: ignore[arg-type]  # from_attributes handles ORM
        session_token=token,
    )


@router.post("/logout", status_code=204)
async def logout(
    request: Request,
    user: User = Depends(get_current_user),
) -> None:
    """Logout -- delete session from Redis. (P-3)"""
    auth_header = request.headers.get("Authorization", "")
    token = auth_header[7:] if auth_header.startswith("Bearer ") else ""
    if token:
        # FIX 2.3: pass user_id to clean up Sorted Set index entry.
        await delete_session(token, user_id=user.id)
    logger.info("user_logout", user_id=str(user.id))


@router.post("/logout-all", status_code=204)
async def logout_all(
    user: User = Depends(get_current_user),
) -> None:
    """Logout all sessions for the current user (W-06).

    Invalidates every active session token. The current request
    succeeds (user is already authenticated), but all subsequent
    requests with any of the user's tokens will fail with 401.
    """
    count = await delete_all_sessions(user.id)
    logger.info(
        "user_logout_all",
        user_id=str(user.id),
        sessions_invalidated=count,
    )
