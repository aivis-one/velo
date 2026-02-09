# =============================================================================
# Test: Users Module — Profile get/update endpoints
# =============================================================================

import hashlib
import hmac
import json
import time
from unittest.mock import patch
from urllib.parse import urlencode

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings

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

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    computed_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    params["hash"] = computed_hash
    return urlencode(params)


async def _login_user(
    client: AsyncClient,
    telegram_id: int = 88001,
    first_name: str = "UserTest",
    username: str = "usertest",
) -> dict:
    """Create a user via POST /auth/telegram and return the response dict."""
    user_data = {"id": telegram_id, "first_name": first_name, "username": username}
    init_data = _build_init_data(user_data)

    with patch.object(settings, "telegram_bot_token", BOT_TOKEN):
        response = await client.post(
            "/api/v1/auth/telegram",
            json={"init_data": init_data},
        )

    assert response.status_code == 200
    return response.json()


def _auth_headers(token: str) -> dict:
    """Build Authorization header."""
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# GET /api/v1/users/me
# ---------------------------------------------------------------------------


async def test_get_me_success(client: AsyncClient) -> None:
    """Authenticated user can retrieve their profile."""
    data = await _login_user(client, telegram_id=88001)
    token = data["session_token"]

    response = await client.get("/api/v1/users/me", headers=_auth_headers(token))

    assert response.status_code == 200
    body = response.json()
    assert body["telegram_id"] == 88001
    assert body["first_name"] == "UserTest"
    assert body["role"] == "user"
    assert body["is_active"] is True
    assert "id" in body
    assert "created_at" in body


async def test_get_me_no_auth(client: AsyncClient) -> None:
    """Request without token → 401."""
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401


async def test_get_me_invalid_token(client: AsyncClient) -> None:
    """Request with garbage token → 401."""
    response = await client.get(
        "/api/v1/users/me",
        headers=_auth_headers("garbage-token"),
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# PATCH /api/v1/users/me
# ---------------------------------------------------------------------------


async def test_update_me_single_field(client: AsyncClient) -> None:
    """Update only first_name — other fields unchanged."""
    data = await _login_user(client, telegram_id=88010, first_name="Before")
    token = data["session_token"]

    response = await client.patch(
        "/api/v1/users/me",
        headers=_auth_headers(token),
        json={"first_name": "After"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["first_name"] == "After"
    assert body["telegram_id"] == 88010

    # Verify persistence — GET should return updated value.
    get_response = await client.get(
        "/api/v1/users/me",
        headers=_auth_headers(token),
    )
    assert get_response.json()["first_name"] == "After"


async def test_update_me_multiple_fields(client: AsyncClient) -> None:
    """Update several fields at once."""
    data = await _login_user(client, telegram_id=88011)
    token = data["session_token"]

    response = await client.patch(
        "/api/v1/users/me",
        headers=_auth_headers(token),
        json={
            "first_name": "Updated",
            "last_name": "Person",
            "timezone": "Europe/Moscow",
            "language": "ru",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["first_name"] == "Updated"
    assert body["last_name"] == "Person"
    assert body["timezone"] == "Europe/Moscow"
    assert body["language"] == "ru"


async def test_update_me_empty_body(client: AsyncClient) -> None:
    """Empty body — no changes, still 200."""
    data = await _login_user(client, telegram_id=88012, first_name="Stable")
    token = data["session_token"]

    response = await client.patch(
        "/api/v1/users/me",
        headers=_auth_headers(token),
        json={},
    )

    assert response.status_code == 200
    assert response.json()["first_name"] == "Stable"


async def test_update_me_set_null(client: AsyncClient) -> None:
    """Explicitly setting a field to null clears it."""
    data = await _login_user(client, telegram_id=88013, first_name="HasName")
    token = data["session_token"]

    response = await client.patch(
        "/api/v1/users/me",
        headers=_auth_headers(token),
        json={"last_name": None},
    )

    assert response.status_code == 200
    assert response.json()["last_name"] is None


async def test_update_me_no_auth(client: AsyncClient) -> None:
    """PATCH without token → 401."""
    response = await client.patch(
        "/api/v1/users/me",
        json={"first_name": "Hacker"},
    )
    assert response.status_code == 401


async def test_update_me_field_too_long(client: AsyncClient) -> None:
    """first_name exceeding max_length → 422."""
    data = await _login_user(client, telegram_id=88014)
    token = data["session_token"]

    response = await client.patch(
        "/api/v1/users/me",
        headers=_auth_headers(token),
        json={"first_name": "A" * 101},
    )

    assert response.status_code == 422
