# =============================================================================
# Test: Auth Module — Telegram validation, sessions, endpoints
# =============================================================================

import hashlib
import hmac
import json
import time
from unittest.mock import patch
from urllib.parse import urlencode

import pytest
from httpx import AsyncClient

from app.modules.auth.service import (
    TelegramValidationError,
    validate_telegram_init_data,
)

BOT_TOKEN = "123456:ABC-DEF"


def _build_init_data(
    user_data: dict,
    bot_token: str = BOT_TOKEN,
    auth_date: int | None = None,
) -> str:
    """Build a valid Telegram initData query string with correct HMAC."""
    if auth_date is None:
        auth_date = int(time.time())

    params = {
        "user": json.dumps(user_data),
        "auth_date": str(auth_date),
    }

    # Compute hash the same way Telegram does.
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    computed_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    params["hash"] = computed_hash
    return urlencode(params)


# ---------------------------------------------------------------------------
# validate_telegram_init_data
# ---------------------------------------------------------------------------


class TestValidateTelegramInitData:
    """Tests for HMAC validation of Telegram initData."""

    def test_valid_init_data(self) -> None:
        user = {"id": 12345, "first_name": "Test"}
        init_data = _build_init_data(user)
        result = validate_telegram_init_data(init_data, BOT_TOKEN)
        assert result["id"] == 12345
        assert result["first_name"] == "Test"

    def test_invalid_hash(self) -> None:
        user = {"id": 12345, "first_name": "Test"}
        init_data = _build_init_data(user) + "&hash=invalidhash"
        # parse_qs takes last value, but let's tamper differently
        init_data = _build_init_data(user, bot_token="wrong-token")
        with pytest.raises(TelegramValidationError, match="signature"):
            validate_telegram_init_data(init_data, BOT_TOKEN)

    def test_missing_hash(self) -> None:
        params = {"user": json.dumps({"id": 1}), "auth_date": str(int(time.time()))}
        init_data = urlencode(params)
        with pytest.raises(TelegramValidationError, match="Missing hash"):
            validate_telegram_init_data(init_data, BOT_TOKEN)

    def test_expired_auth_date(self) -> None:
        user = {"id": 12345, "first_name": "Test"}
        old_time = int(time.time()) - 600  # 10 minutes ago
        init_data = _build_init_data(user, auth_date=old_time)
        with pytest.raises(TelegramValidationError, match="expired"):
            validate_telegram_init_data(init_data, BOT_TOKEN)

    def test_missing_user(self) -> None:
        auth_date = str(int(time.time()))
        params = {"auth_date": auth_date}
        data_check_string = f"auth_date={auth_date}"
        secret_key = hmac.new(
            b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256
        ).digest()
        h = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        params["hash"] = h
        init_data = urlencode(params)
        with pytest.raises(TelegramValidationError, match="Missing user"):
            validate_telegram_init_data(init_data, BOT_TOKEN)

    def test_invalid_auth_date_format(self) -> None:
        """P-11: non-numeric auth_date should raise, not crash with 500."""
        user = {"id": 12345}
        params = {
            "user": json.dumps(user),
            "auth_date": "not-a-number",
        }
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))
        secret_key = hmac.new(
            b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256
        ).digest()
        h = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        params["hash"] = h
        init_data = urlencode(params)
        with pytest.raises(TelegramValidationError, match="Invalid auth_date"):
            validate_telegram_init_data(init_data, BOT_TOKEN)


# ---------------------------------------------------------------------------
# POST /api/v1/auth/telegram
# ---------------------------------------------------------------------------


async def test_auth_telegram_success(client: AsyncClient) -> None:
    """Full auth flow: valid initData → user created → token returned."""
    user_data = {"id": 99999, "first_name": "Tester", "username": "tester"}
    init_data = _build_init_data(user_data)

    with patch("app.modules.auth.router.settings") as mock_settings:
        mock_settings.telegram_bot_token = BOT_TOKEN
        response = await client.post(
            "/api/v1/auth/telegram",
            json={"init_data": init_data},
        )

    assert response.status_code == 200
    data = response.json()
    assert "session_token" in data
    assert data["user"]["telegram_id"] == 99999
    assert data["user"]["first_name"] == "Tester"


async def test_auth_telegram_invalid_data(client: AsyncClient) -> None:
    """Invalid initData → 400."""
    response = await client.post(
        "/api/v1/auth/telegram",
        json={"init_data": "garbage=data&hash=fake"},
    )
    assert response.status_code == 400
