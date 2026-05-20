# =============================================================================
# Test: Users Module — Profile get/update endpoints
# =============================================================================

import pytest
from httpx import AsyncClient

from tests.helpers import auth_headers, login_user


# ---------------------------------------------------------------------------
# GET /api/v1/users/me
# ---------------------------------------------------------------------------


async def test_get_me_success(client: AsyncClient) -> None:
    """Authenticated user can retrieve their profile."""
    data = await login_user(client, telegram_id=88001, first_name="UserTest")
    token = data["session_token"]

    response = await client.get("/api/v1/users/me", headers=auth_headers(token))

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
        headers=auth_headers("garbage-token"),
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# PATCH /api/v1/users/me
# ---------------------------------------------------------------------------


async def test_update_me_single_field(client: AsyncClient) -> None:
    """Update only first_name — other fields unchanged."""
    data = await login_user(client, telegram_id=88010, first_name="Before")
    token = data["session_token"]

    response = await client.patch(
        "/api/v1/users/me",
        headers=auth_headers(token),
        json={"first_name": "After"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["first_name"] == "After"
    assert body["telegram_id"] == 88010

    # Verify persistence — GET should return updated value.
    get_response = await client.get(
        "/api/v1/users/me",
        headers=auth_headers(token),
    )
    assert get_response.json()["first_name"] == "After"


async def test_update_me_multiple_fields(client: AsyncClient) -> None:
    """Update several fields at once."""
    data = await login_user(client, telegram_id=88011)
    token = data["session_token"]

    response = await client.patch(
        "/api/v1/users/me",
        headers=auth_headers(token),
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
    data = await login_user(client, telegram_id=88012, first_name="Stable")
    token = data["session_token"]

    response = await client.patch(
        "/api/v1/users/me",
        headers=auth_headers(token),
        json={},
    )

    assert response.status_code == 200
    assert response.json()["first_name"] == "Stable"


async def test_update_me_set_null(client: AsyncClient) -> None:
    """Explicitly setting a field to null clears it."""
    data = await login_user(client, telegram_id=88013, first_name="HasName")
    token = data["session_token"]

    response = await client.patch(
        "/api/v1/users/me",
        headers=auth_headers(token),
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
    data = await login_user(client, telegram_id=88014)
    token = data["session_token"]

    response = await client.patch(
        "/api/v1/users/me",
        headers=auth_headers(token),
        json={"first_name": "A" * 101},
    )

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# PATCH /api/v1/users/me — empty string validation (F-1)
# ---------------------------------------------------------------------------


async def test_update_me_empty_string_first_name(client: AsyncClient) -> None:
    """Empty string for first_name → 422 (use null to clear)."""
    data = await login_user(client, telegram_id=88020)
    token = data["session_token"]

    response = await client.patch(
        "/api/v1/users/me",
        headers=auth_headers(token),
        json={"first_name": ""},
    )

    assert response.status_code == 422


async def test_update_me_empty_string_timezone(client: AsyncClient) -> None:
    """Empty string for timezone → 422."""
    data = await login_user(client, telegram_id=88021)
    token = data["session_token"]

    response = await client.patch(
        "/api/v1/users/me",
        headers=auth_headers(token),
        json={"timezone": ""},
    )

    assert response.status_code == 422


async def test_update_me_empty_string_language(client: AsyncClient) -> None:
    """Empty string for language → 422."""
    data = await login_user(client, telegram_id=88022)
    token = data["session_token"]

    response = await client.patch(
        "/api/v1/users/me",
        headers=auth_headers(token),
        json={"language": ""},
    )

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Onboarding flag (stored in credentials JSONB, surfaced as a bool)
# ---------------------------------------------------------------------------


async def test_onboarding_completed_defaults_false_for_new_user(
    client: AsyncClient,
) -> None:
    """A freshly created user has onboarding_completed=False (key absent)."""
    data = await login_user(client, telegram_id=88030, first_name="Newbie")
    token = data["session_token"]

    response = await client.get("/api/v1/users/me", headers=auth_headers(token))

    assert response.status_code == 200
    assert response.json()["onboarding_completed"] is False


async def test_onboarding_completed_can_be_set_true(
    client: AsyncClient,
) -> None:
    """PATCH onboarding_completed=true is persisted and returned."""
    data = await login_user(client, telegram_id=88031, first_name="Finisher")
    token = data["session_token"]

    patch_response = await client.patch(
        "/api/v1/users/me",
        headers=auth_headers(token),
        json={"onboarding_completed": True},
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["onboarding_completed"] is True

    # Persisted: a fresh GET still reports it true.
    get_response = await client.get(
        "/api/v1/users/me",
        headers=auth_headers(token),
    )
    assert get_response.json()["onboarding_completed"] is True


async def test_onboarding_completed_survives_relogin(
    client: AsyncClient,
) -> None:
    """The key invariant: re-login MUST preserve onboarding_completed.

    upsert_user_on_login merges credentials (coalesce(...) || fresh) instead
    of overwriting, so the flag set via PATCH is not wiped when the same
    Telegram user logs in again. Regression guard for the welcome flow.
    """
    # First login + finish onboarding.
    first = await login_user(client, telegram_id=88032, first_name="Returner")
    token1 = first["session_token"]
    await client.patch(
        "/api/v1/users/me",
        headers=auth_headers(token1),
        json={"onboarding_completed": True},
    )

    # Re-login with the SAME telegram_id (build_init_data adds a unique
    # query_id, so anti-replay is not triggered).
    second = await login_user(client, telegram_id=88032, first_name="Returner")
    token2 = second["session_token"]

    # The flag must still be true after the upsert (UPDATE branch / merge).
    me = await client.get("/api/v1/users/me", headers=auth_headers(token2))
    assert me.status_code == 200
    assert me.json()["onboarding_completed"] is True


async def test_onboarding_completed_relogin_refreshes_telegram_fields(
    client: AsyncClient,
) -> None:
    """Merge keeps the flag AND refreshes Telegram-sourced fields on re-login."""
    first = await login_user(
        client, telegram_id=88033, first_name="Before", username="before",
    )
    token1 = first["session_token"]
    await client.patch(
        "/api/v1/users/me",
        headers=auth_headers(token1),
        json={"onboarding_completed": True},
    )

    # Re-login with a changed first_name (Telegram profile updated).
    second = await login_user(
        client, telegram_id=88033, first_name="After", username="after",
    )
    token2 = second["session_token"]

    me = await client.get("/api/v1/users/me", headers=auth_headers(token2))
    body = me.json()
    # Flag preserved from credentials...
    assert body["onboarding_completed"] is True
    # ...and the column field synced from the fresh Telegram payload.
    assert body["first_name"] == "After"


async def test_onboarding_completed_null_does_not_reset_flag(
    client: AsyncClient,
) -> None:
    """PATCH onboarding_completed=null is ignored, not written as null.

    Service drops None for JSONB-backed fields, so a once-true flag stays
    true rather than being overwritten with null (bool(None) -> False).
    """
    data = await login_user(client, telegram_id=88034, first_name="NullTest")
    token = data["session_token"]

    # Set it true first.
    await client.patch(
        "/api/v1/users/me",
        headers=auth_headers(token),
        json={"onboarding_completed": True},
    )

    # Now send null -- should be a no-op for the flag.
    resp = await client.patch(
        "/api/v1/users/me",
        headers=auth_headers(token),
        json={"onboarding_completed": None},
    )
    assert resp.status_code == 200
    assert resp.json()["onboarding_completed"] is True
