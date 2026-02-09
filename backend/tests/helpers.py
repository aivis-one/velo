# =============================================================================
# VELO Backend — Shared Test Helpers
# =============================================================================
#
# Utility functions used across multiple test files.
# Not a conftest (no fixtures here) — just plain functions.
# =============================================================================

import hashlib
import hmac
import json
import time
from unittest.mock import patch
from urllib.parse import urlencode

from httpx import AsyncClient

from app.core.config import settings

BOT_TOKEN = "123456:ABC-DEF"


def build_init_data(
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

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    computed_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    params["hash"] = computed_hash
    return urlencode(params)


async def login_user(
    client: AsyncClient,
    telegram_id: int = 77001,
    first_name: str = "TestUser",
    username: str = "testuser",
) -> dict:
    """Create a user via POST /auth/telegram and return the response dict.

    Uses real PostgreSQL and Redis (runs on test VPS).
    Only patches telegram_bot_token for HMAC validation.
    """
    user_data = {"id": telegram_id, "first_name": first_name, "username": username}
    init_data = build_init_data(user_data)

    with patch.object(settings, "telegram_bot_token", BOT_TOKEN):
        response = await client.post(
            "/api/v1/auth/telegram",
            json={"init_data": init_data},
        )

    assert response.status_code == 200
    return response.json()


def auth_headers(token: str) -> dict:
    """Build Authorization header."""
    return {"Authorization": f"Bearer {token}"}
