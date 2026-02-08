# =============================================================================
# VELO Backend — Auth Router
# =============================================================================
#
# ENDPOINTS:
#   POST /api/v1/auth/telegram — Login via Telegram WebApp initData
# =============================================================================

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db_session
from app.core.exceptions import BadRequestError
from app.modules.auth.schemas import AuthResponse, TelegramAuthRequest
from app.modules.auth.service import (
    TelegramValidationError,
    create_session,
    upsert_user_on_login,
    validate_telegram_init_data,
)

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
      3. Create session in Redis (token, TTL 30 days)
      4. Return user + session_token
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

    # Create session in Redis.
    token = await create_session(user)

    return AuthResponse(
        user=user,  # type: ignore[arg-type]  # from_attributes handles ORM
        session_token=token,
    )
