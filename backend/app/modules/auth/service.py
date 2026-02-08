# =============================================================================
# VELO Backend — Auth Service
# =============================================================================
#
# RESPONSIBILITIES:
#   1. Validate Telegram WebApp initData (HMAC-SHA256)
#   2. Create or update User on login
#   3. Manage sessions in Redis (create / get / delete)
#
# TELEGRAM initData VALIDATION:
#   Telegram sends a query string signed with HMAC-SHA256.
#   We verify the signature using our bot token to ensure the data
#   is authentic and not forged. See:
#   https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
#
# SESSION FORMAT IN REDIS:
#   Key:   session:{token}
#   Value: JSON {"user_id": "uuid", "telegram_id": 123, "created_at": "iso"}
#   TTL:   30 days (configurable via SESSION_TTL_DAYS)
# =============================================================================

import hashlib
import hmac
import json
import secrets
from datetime import UTC, datetime
from urllib.parse import parse_qs, unquote

import structlog
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.redis import get_redis
from app.modules.users.models import User

logger = structlog.get_logger()

# Session key prefix in Redis.
_SESSION_PREFIX = "session:"


def _get_session_ttl() -> int:
    """Session TTL in seconds, computed at call time (not import time).

    TD-021: previously this was a module-level constant computed at import.
    Tests could not override SESSION_TTL_DAYS because the value was already
    baked in. Now it reads settings.session_ttl_days on every call.
    """
    return settings.session_ttl_days * 24 * 60 * 60


# ---------------------------------------------------------------------------
# Telegram initData validation
# ---------------------------------------------------------------------------


class TelegramValidationError(Exception):
    """Raised when initData signature or content is invalid."""


def validate_telegram_init_data(init_data: str, bot_token: str) -> dict:
    """Validate and parse Telegram WebApp initData.

    Args:
        init_data: Raw query string from Telegram WebApp.
        bot_token: Bot token from BotFather.

    Returns:
        Parsed user data dict from Telegram.

    Raises:
        TelegramValidationError: If signature is invalid or data expired.
    """
    # Parse the query string into key-value pairs.
    parsed = parse_qs(init_data, keep_blank_values=True)

    # Extract hash — Telegram includes it for verification.
    received_hash = parsed.pop("hash", [None])[0]
    if not received_hash:
        raise TelegramValidationError("Missing hash in initData")

    # Build the data-check-string: sorted key=value pairs joined by \n.
    # Each value is taken as-is (first element of the list from parse_qs).
    data_check_pairs = sorted(f"{k}={v[0]}" for k, v in parsed.items())
    data_check_string = "\n".join(data_check_pairs)

    # Compute HMAC-SHA256:
    # 1. secret_key = HMAC-SHA256("WebAppData", bot_token)
    # 2. hash = HMAC-SHA256(secret_key, data_check_string)
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    computed_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    # Compare hashes (constant-time to prevent timing attacks).
    if not hmac.compare_digest(computed_hash, received_hash):
        raise TelegramValidationError("Invalid initData signature")

    # Check auth_date is not too old (5 minutes).
    auth_date_str = parsed.get("auth_date", [None])[0]
    if not auth_date_str:
        raise TelegramValidationError("Missing auth_date")

    try:
        auth_date = int(auth_date_str)
    except ValueError:
        raise TelegramValidationError("Invalid auth_date format") from None

    now = int(datetime.now(UTC).timestamp())
    if now - auth_date > 300:  # 5 minutes
        raise TelegramValidationError("initData expired")

    # Parse user JSON from the query string.
    user_data_str = parsed.get("user", [None])[0]
    if not user_data_str:
        raise TelegramValidationError("Missing user in initData")

    user_data = json.loads(unquote(user_data_str))
    return user_data


# ---------------------------------------------------------------------------
# User upsert (create or update on login)
# ---------------------------------------------------------------------------


async def upsert_user_on_login(
    telegram_user: dict,
    session: AsyncSession,
) -> User:
    """Find user by telegram_id or create a new one. Update profile on login.

    Uses INSERT ... ON CONFLICT DO UPDATE (P-1) to avoid race conditions
    when two requests arrive simultaneously for a new user.

    Args:
        telegram_user: Parsed user dict from Telegram initData.
        session: Database session (read-write).

    Returns:
        User object (new or existing, updated).
    """
    telegram_id = telegram_user["id"]
    now = datetime.now(UTC)

    credentials = {
        "telegram_username": telegram_user.get("username"),
        "telegram_photo_url": telegram_user.get("photo_url"),
    }

    # Atomic upsert: INSERT or UPDATE in a single statement.
    # No race condition possible — PostgreSQL locks the row on conflict.
    stmt = (
        pg_insert(User)
        .values(
            telegram_id=telegram_id,
            first_name=telegram_user.get("first_name"),
            last_name=telegram_user.get("last_name"),
            avatar_url=telegram_user.get("photo_url"),
            language=telegram_user.get("language_code", "en"),
            credentials=credentials,
            last_login_at=now,
        )
        .on_conflict_do_update(
            index_elements=["telegram_id"],
            set_={
                "first_name": telegram_user.get("first_name"),
                "last_name": telegram_user.get("last_name"),
                "avatar_url": telegram_user.get("photo_url"),
                "credentials": credentials,
                "last_login_at": now,
            },
        )
        .returning(User)
    )

    result = await session.execute(stmt)
    user = result.scalar_one()

    logger.info(
        "user_upserted",
        telegram_id=telegram_id,
        user_id=str(user.id),
    )

    return user


# ---------------------------------------------------------------------------
# Session management (Redis)
# ---------------------------------------------------------------------------


async def create_session(user: User) -> str:
    """Create a new session in Redis and return the token.

    Token is a cryptographically random 64-char string.
    """
    token = secrets.token_urlsafe(48)
    redis = get_redis()

    session_data = json.dumps(
        {
            "user_id": str(user.id),
            "telegram_id": user.telegram_id,
            "created_at": datetime.now(UTC).isoformat(),
        }
    )

    await redis.set(
        f"{_SESSION_PREFIX}{token}",
        session_data,
        ex=_get_session_ttl(),
    )

    logger.info("session_created", user_id=str(user.id))
    return token


async def get_session(token: str) -> dict | None:
    """Retrieve session data from Redis by token.

    Returns None if token is invalid or expired.
    """
    redis = get_redis()
    data = await redis.get(f"{_SESSION_PREFIX}{token}")

    if data is None:
        return None

    return json.loads(data)


async def delete_session(token: str) -> None:
    """Delete a session from Redis (logout)."""
    redis = get_redis()
    await redis.delete(f"{_SESSION_PREFIX}{token}")
