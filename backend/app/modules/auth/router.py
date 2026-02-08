# =============================================================================
# VELO Backend — Auth Router
# =============================================================================
#
# ENDPOINTS:
#   POST /api/v1/auth/telegram — Login via Telegram WebApp initData
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
    create_session,
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
      2. Find or create User by telegram_id
      3. Commit DB changes (P-2: before Redis to avoid ghost sessions)
      4. Create session in Redis (token, TTL 30 days)
      5. Return user + session_token
    """
    # Validate initData from Telegram.
    try:
        telegram_user = validate_telegram_init_data(
            body.init_data,
            settings.telegram_bot_token,
        )
    except TelegramValidationError as e:
        logger.warning("telegram_auth_failed", reason=str(e))
        raise BadRequestError(str(e)) from e

    # Create or update user.
    user = await upsert_user_on_login(telegram_user, session)

    # P-2: commit DB first. If commit fails, no orphan session in Redis.
    # get_db_session auto-commits on success, but we need it NOW before Redis.
    await session.commit()

    # Create session in Redis.
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
    """Logout — delete session from Redis. (P-3)"""
    auth_header = request.headers.get("Authorization", "")
    token = auth_header[7:] if auth_header.startswith("Bearer ") else ""
    if token:
        await delete_session(token)
    logger.info("user_logout", user_id=str(user.id))
