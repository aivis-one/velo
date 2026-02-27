# =============================================================================
# Test: Auth Module — Telegram validation, sessions, endpoints
# =============================================================================

import hashlib
import hmac
import json
import time
from unittest.mock import AsyncMock, MagicMock, patch
from urllib.parse import urlencode

import pytest
from httpx import AsyncClient
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.auth.service import (
    TelegramValidationError,
    validate_telegram_init_data,
)
from app.modules.users.models import User
from tests.helpers import BOT_TOKEN, auth_headers, build_init_data, login_user


# ---------------------------------------------------------------------------
# validate_telegram_init_data
# ---------------------------------------------------------------------------


class TestValidateTelegramInitData:
    """Tests for HMAC validation of Telegram initData."""

    def test_valid_data(self) -> None:
        """Correctly signed initData passes validation."""
        user_data = {"id": 12345, "first_name": "Test"}
        init_data = build_init_data(user_data)
        result = validate_telegram_init_data(init_data, BOT_TOKEN)
        assert result["id"] == 12345

    def test_missing_hash(self) -> None:
        """initData without hash → error."""
        with pytest.raises(TelegramValidationError, match="Missing hash"):
            validate_telegram_init_data("user=%7B%7D&auth_date=123", BOT_TOKEN)

    def test_invalid_hash(self) -> None:
        """Tampered hash → error."""
        user_data = {"id": 12345, "first_name": "Test"}
        init_data = build_init_data(user_data)
        # Replace hash with garbage.
        tampered = init_data.rsplit("hash=", 1)[0] + "hash=deadbeef"
        with pytest.raises(TelegramValidationError, match="Invalid initData signature"):
            validate_telegram_init_data(tampered, BOT_TOKEN)

    def test_wrong_bot_token(self) -> None:
        """Different bot token → signature mismatch."""
        user_data = {"id": 12345, "first_name": "Test"}
        init_data = build_init_data(user_data, bot_token=BOT_TOKEN)
        with pytest.raises(TelegramValidationError, match="Invalid initData signature"):
            validate_telegram_init_data(init_data, "999999:WRONG-TOKEN")

    def test_expired_data(self) -> None:
        """auth_date older than 5 minutes → error."""
        user_data = {"id": 12345, "first_name": "Test"}
        old_date = int(time.time()) - 600  # 10 minutes ago
        init_data = build_init_data(user_data, auth_date=old_date)
        with pytest.raises(TelegramValidationError, match="expired"):
            validate_telegram_init_data(init_data, BOT_TOKEN)

    def test_missing_auth_date(self) -> None:
        """initData without auth_date → error."""
        # Build manually without auth_date.
        params = {"user": json.dumps({"id": 1})}
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))
        secret_key = hmac.new(
            b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256
        ).digest()
        h = hmac.new(
            secret_key, data_check_string.encode(), hashlib.sha256
        ).hexdigest()
        params["hash"] = h
        init_data = urlencode(params)
        with pytest.raises(TelegramValidationError, match="Missing auth_date"):
            validate_telegram_init_data(init_data, BOT_TOKEN)

    def test_missing_user(self) -> None:
        """initData without user field → error."""
        params = {"auth_date": str(int(time.time()))}
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))
        secret_key = hmac.new(
            b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256
        ).digest()
        h = hmac.new(
            secret_key, data_check_string.encode(), hashlib.sha256
        ).hexdigest()
        params["hash"] = h
        init_data = urlencode(params)
        with pytest.raises(TelegramValidationError, match="Missing user"):
            validate_telegram_init_data(init_data, BOT_TOKEN)


# ---------------------------------------------------------------------------
# POST /api/v1/auth/telegram
# ---------------------------------------------------------------------------


async def test_auth_telegram_success_mocked_redis(client: AsyncClient) -> None:
    """Full auth flow with mocked Redis (unit-test style)."""
    user_data = {"id": 99999, "first_name": "Tester", "username": "tester"}
    init_data = build_init_data(user_data)

    with (
        patch("app.modules.auth.router.settings") as mock_settings,
        patch("app.modules.auth.service.get_redis") as mock_get_redis,
    ):
        mock_settings.telegram_bot_token = BOT_TOKEN

        # CRITICAL-05: create_session now uses pipeline(transaction=True).
        # redis.pipeline() is a SYNC call returning a Pipeline object.
        # Pipeline methods (.set, .zadd, etc.) are also sync (they queue).
        # Only .execute() is async (sends MULTI/EXEC to Redis).
        mock_pipe = MagicMock()
        mock_pipe.set = MagicMock(return_value=mock_pipe)
        mock_pipe.zadd = MagicMock(return_value=mock_pipe)
        mock_pipe.zremrangebyscore = MagicMock(return_value=mock_pipe)
        mock_pipe.expire = MagicMock(return_value=mock_pipe)
        # execute() returns list of results; [2] is zremrangebyscore count.
        mock_pipe.execute = AsyncMock(return_value=[True, 1, 0, True])

        mock_redis = MagicMock()
        mock_redis.pipeline = MagicMock(return_value=mock_pipe)
        mock_get_redis.return_value = mock_redis

        response = await client.post(
            "/api/v1/auth/telegram",
            json={"init_data": init_data},
        )

    assert response.status_code == 200
    data = response.json()
    assert "session_token" in data
    assert data["user"]["telegram_id"] == 99999
    assert data["user"]["first_name"] == "Tester"
    # Verify pipeline was used to store session atomically.
    mock_redis.pipeline.assert_called_once_with(transaction=True)
    mock_pipe.set.assert_called_once()
    mock_pipe.execute.assert_awaited_once()


async def test_auth_telegram_invalid_data(client: AsyncClient) -> None:
    """Invalid initData → 400."""
    response = await client.post(
        "/api/v1/auth/telegram",
        json={"init_data": "garbage=data&hash=fake"},
    )
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# POST /api/v1/auth/logout (TD-020)
# ---------------------------------------------------------------------------


async def test_logout_success(client: AsyncClient) -> None:
    """Logout deletes session; same token becomes invalid afterward."""
    data = await login_user(client, telegram_id=77001, first_name="AuthTest")
    token = data["session_token"]

    response = await client.post(
        "/api/v1/auth/logout",
        headers=auth_headers(token),
    )
    assert response.status_code == 204

    # Same token should now be rejected (session deleted from Redis).
    response = await client.post(
        "/api/v1/auth/logout",
        headers=auth_headers(token),
    )
    assert response.status_code == 401


async def test_logout_no_token(client: AsyncClient) -> None:
    """Logout without Authorization header → 401."""
    response = await client.post("/api/v1/auth/logout")
    assert response.status_code == 401


async def test_logout_invalid_token(client: AsyncClient) -> None:
    """Logout with garbage token → 401 (session not found in Redis)."""
    response = await client.post(
        "/api/v1/auth/logout",
        headers=auth_headers("garbage-token-that-does-not-exist"),
    )
    assert response.status_code == 401


async def test_logout_inactive_user(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Deactivated user cannot access protected endpoints → 403."""
    data = await login_user(client, telegram_id=77002, first_name="Inactive")
    token = data["session_token"]
    user_id = data["user"]["id"]

    # Deactivate user directly in DB.
    stmt = update(User).where(User.id == user_id).values(is_active=False)
    await db_session.execute(stmt)
    await db_session.commit()

    # Token is valid in Redis, but user is inactive → 403.
    response = await client.post(
        "/api/v1/auth/logout",
        headers=auth_headers(token),
    )
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# POST /api/v1/auth/logout-all (W-06)
# ---------------------------------------------------------------------------


async def test_logout_all_invalidates_all_sessions(
    client: AsyncClient,
) -> None:
    """logout-all invalidates every session for the user."""
    # Create two sessions for the same user.
    data1 = await login_user(client, telegram_id=77010, first_name="Multi")
    data2 = await login_user(client, telegram_id=77010, first_name="Multi")
    token1 = data1["session_token"]
    token2 = data2["session_token"]

    # Both tokens work.
    r1 = await client.get("/api/v1/users/me", headers=auth_headers(token1))
    r2 = await client.get("/api/v1/users/me", headers=auth_headers(token2))
    assert r1.status_code == 200
    assert r2.status_code == 200

    # Logout-all using token1.
    response = await client.post(
        "/api/v1/auth/logout-all",
        headers=auth_headers(token1),
    )
    assert response.status_code == 204

    # Both tokens should now be invalid.
    r1 = await client.get("/api/v1/users/me", headers=auth_headers(token1))
    r2 = await client.get("/api/v1/users/me", headers=auth_headers(token2))
    assert r1.status_code == 401
    assert r2.status_code == 401


async def test_logout_all_other_user_unaffected(
    client: AsyncClient,
) -> None:
    """logout-all for user A does not affect user B."""
    data_a = await login_user(client, telegram_id=77020, first_name="UserA")
    data_b = await login_user(client, telegram_id=77021, first_name="UserB")
    token_a = data_a["session_token"]
    token_b = data_b["session_token"]

    # Logout-all for user A.
    response = await client.post(
        "/api/v1/auth/logout-all",
        headers=auth_headers(token_a),
    )
    assert response.status_code == 204

    # User A is logged out.
    r_a = await client.get("/api/v1/users/me", headers=auth_headers(token_a))
    assert r_a.status_code == 401

    # User B is unaffected.
    r_b = await client.get("/api/v1/users/me", headers=auth_headers(token_b))
    assert r_b.status_code == 200
