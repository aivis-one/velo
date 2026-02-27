# =============================================================================
# VELO Backend -- Auth Service (updated Phase 7.3, FIX 2.2 + 2.3, QW-1, HIGH-1)
# =============================================================================
#
# RESPONSIBILITIES:
#   1. Validate Telegram WebApp initData (HMAC-SHA256)
#   2. Create or update User on login
#   3. Manage sessions in Redis (create / get / delete / delete-all)
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
#
# SESSION INDEX (W-06, FIX 2.3):
#   Key:   user_sessions:{user_id}
#   Type:  Redis ZSET (Sorted Set), score = creation timestamp
#   TTL:   Same as session TTL
#   Purpose: Reverse index for logout-all. Sorted Set allows efficient
#            GC of expired tokens via ZREMRANGEBYSCORE on each login.
#            Prevents unbounded memory growth from dead session entries.
# =============================================================================

import hashlib
import hmac
import json
import secrets
from datetime import UTC, datetime
from urllib.parse import parse_qs, unquote
from uuid import UUID

import structlog
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.redis import get_redis
from app.modules.notifications.template_engine import normalize_language
from app.modules.users.models import User

logger = structlog.get_logger()

# Session key prefix in Redis.
_SESSION_PREFIX = "session:"

# Reverse index prefix: ZSET of tokens per user (W-06, FIX 2.3).
_USER_SESSIONS_PREFIX = "user_sessions:"

# HIGH-1: Maximum clock skew tolerance for auth_date (seconds).
# Rejects initData with auth_date more than 60s in the future,
# which would bypass the 5-minute expiry check.
_MAX_CLOCK_SKEW = 60


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

    # Extract hash -- Telegram includes it for verification.
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

    # HIGH-1: Reject auth_date from the future (clock skew tolerance 60s).
    # Without this, an attacker can set auth_date far in the future,
    # making the token valid indefinitely (now - future_date < 0 < 300).
    if auth_date > now + _MAX_CLOCK_SKEW:
        raise TelegramValidationError("initData auth_date is in the future")

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

    Phase 7.3: normalizes language_code from Telegram to supported set
    (en/de/es/ru). Unsupported codes fall back to "en".

    FIX 2.2: language is set only on INSERT (new users). Returning users
    keep their language preference set via PATCH /users/me.

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
        "language_code": telegram_user.get("language_code"),
    }

    # Phase 7.3: Normalize language_code to supported set (en/de/es/ru).
    # Handles "en-US" -> "en", "pt-BR" -> "en" (unsupported -> fallback).
    normalized_lang = normalize_language(
        telegram_user.get("language_code"),
    )

    # Atomic upsert: INSERT or UPDATE in a single statement.
    # No race condition possible -- PostgreSQL locks the row on conflict.
    stmt = (
        pg_insert(User)
        .values(
            telegram_id=telegram_id,
            first_name=telegram_user.get("first_name"),
            last_name=telegram_user.get("last_name"),
            avatar_url=telegram_user.get("photo_url"),
            language=normalized_lang,
            credentials=credentials,
            last_login_at=now,
        )
        .on_conflict_do_update(
            index_elements=["telegram_id"],
            # FIX 2.2: language removed from set_ -- preserve user edits
            # via PATCH /users/me. Language is set on INSERT (new users)
            # but not overwritten on UPDATE (returning users).
            # first_name, last_name, avatar_url sync from Telegram.
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
    Also registers the token in the user's session index (W-06)
    so logout-all can find and invalidate all sessions.

    FIX 2.3: Session index uses Sorted Set (ZSET) with creation
    timestamp as score instead of plain SET. On each login, expired
    tokens are garbage-collected via ZREMRANGEBYSCORE to prevent
    unbounded memory growth.

    CRITICAL-05: All Redis writes (SET + ZADD + ZREMRANGEBYSCORE + EXPIRE)
    are executed in a single MULTI/EXEC pipeline for atomicity.
    Without this, a crash between SET and ZADD could create an
    orphan session not tracked by the index.
    """
    token = secrets.token_urlsafe(48)
    redis = get_redis()
    ttl = _get_session_ttl()
    now = datetime.now(UTC)
    now_ts = now.timestamp()

    session_data = json.dumps(
        {
            "user_id": str(user.id),
            "telegram_id": user.telegram_id,
            "created_at": now.isoformat(),
        }
    )

    session_key = f"{_SESSION_PREFIX}{token}"
    index_key = f"{_USER_SESSIONS_PREFIX}{user.id}"

    # GC cutoff: remove tokens whose creation time is older than TTL.
    # These sessions have expired by Redis TTL but their entries
    # remain in the Sorted Set.
    cutoff = now_ts - ttl

    # CRITICAL-05: MULTI/EXEC pipeline for atomic session creation.
    # All four operations execute as a single atomic unit.
    pipe = redis.pipeline(transaction=True)
    pipe.set(session_key, session_data, ex=ttl)
    pipe.zadd(index_key, {token: now_ts})
    pipe.zremrangebyscore(index_key, "-inf", cutoff)
    pipe.expire(index_key, ttl)
    results = await pipe.execute()

    # results[2] is the count of removed expired tokens from GC.
    removed = results[2]
    if removed:
        logger.debug(
            "session_index_gc",
            user_id=str(user.id),
            removed=removed,
        )

    logger.info("session_created", user_id=str(user.id))
    return token


async def get_session(token: str) -> dict | None:
    """Retrieve session data from Redis by token.

    Returns parsed dict or None if session expired/doesn't exist.
    """
    redis = get_redis()
    data = await redis.get(f"{_SESSION_PREFIX}{token}")
    if data is None:
        return None
    return json.loads(data)


async def delete_session(token: str, user_id: UUID | None = None) -> None:
    """Delete a single session from Redis.

    FIX 2.3: Also removes token from user's Sorted Set index
    if user_id is provided. Prevents stale entries in the index.
    """
    redis = get_redis()
    await redis.delete(f"{_SESSION_PREFIX}{token}")

    # Clean up index entry if we know the user.
    if user_id is not None:
        index_key = f"{_USER_SESSIONS_PREFIX}{user_id}"
        await redis.zrem(index_key, token)

    logger.info("session_deleted")


async def delete_all_sessions(user_id: UUID) -> int:
    """Delete all sessions for a user (W-06: logout-all).

    FIX 2.3: Uses ZRANGE on Sorted Set index to find all tokens,
    then deletes session keys + index atomically via pipeline.

    QW-1: pipeline(transaction=True) wraps commands in MULTI/EXEC
    for true atomicity. Without it, a concurrent create_session could
    add a token to the index between the two DELETEs, losing it.

    Returns:
        Number of sessions deleted.
    """
    redis = get_redis()
    index_key = f"{_USER_SESSIONS_PREFIX}{user_id}"

    # Get all tokens from the Sorted Set index.
    tokens = await redis.zrange(index_key, 0, -1)
    if not tokens:
        return 0

    # QW-1: MULTI/EXEC pipeline for atomic delete.
    session_keys = [f"{_SESSION_PREFIX}{t}" for t in tokens]
    pipe = redis.pipeline(transaction=True)
    pipe.delete(*session_keys)
    pipe.delete(index_key)
    await pipe.execute()

    logger.info(
        "all_sessions_deleted",
        user_id=str(user_id),
        count=len(tokens),
    )

    return len(tokens)
