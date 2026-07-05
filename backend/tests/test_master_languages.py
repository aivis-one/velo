# =============================================================================
# Test: Master languages (E16 -- additive JSONB, freely editable)
# =============================================================================
#
# Covers:
#   - languages captured on apply -> surfaced on GET /masters/me
#   - PATCH /masters/me/languages replaces the set (freely, no moderation)
#   - empty list clears; over-cap is rejected
#
# telegram_id range (56700-56799 -- this module owns this sub-range):
#   56701  -- verified master (default)
#   56790  -- admin (ADMIN_TID)
# =============================================================================

from collections.abc import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import User, UserRole
from tests.helpers import auth_headers, full_cleanup_range, login_user

APPLY_URL = "/api/v1/masters/apply"
VERIFY_URL = "/api/v1/admin/masters/{user_id}/verify"
ME_URL = "/api/v1/masters/me"
LANGUAGES_URL = "/api/v1/masters/me/languages"

ADMIN_TID = 56790


@pytest.fixture(autouse=True)
async def cleanup(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    await _do_cleanup(db_session)
    yield
    await _do_cleanup(db_session)


async def _do_cleanup(session: AsyncSession) -> None:
    await full_cleanup_range(session, 56700, 56799, delete_users=False)
    await session.commit()


def _apply_body(languages: list[str] | None = None) -> dict:
    experience = {
        "methods": ["Медитация"],
        "experience_years": 3,
        "bio": "hi",
        "certifications": [],
    }
    if languages is not None:
        experience["languages"] = languages
    return {
        "profile": {
            "display_name": "Lang Master",
            "email": "lm@test.com",
            "phone": None,
        },
        "experience": experience,
        "documents": [],
    }


async def _make_verified_master(
    client: AsyncClient,
    db_session: AsyncSession,
    *,
    languages: list[str] | None = None,
    telegram_id: int = 56701,
) -> dict:
    auth = await login_user(client, telegram_id=telegram_id, first_name="Master")
    await client.post(
        APPLY_URL,
        json=_apply_body(languages),
        headers=auth_headers(auth["session_token"]),
    )
    await login_user(client, telegram_id=ADMIN_TID, first_name="Admin")
    await db_session.execute(
        update(User)
        .where(User.telegram_id == ADMIN_TID)
        .values(role=UserRole.ADMIN.value)
    )
    await db_session.commit()
    admin_auth = await login_user(client, telegram_id=ADMIN_TID, first_name="Admin")
    verify = await client.post(
        VERIFY_URL.format(user_id=auth["user"]["id"]),
        json={},
        headers=auth_headers(admin_auth["session_token"]),
    )
    assert verify.status_code == 200
    return await login_user(client, telegram_id=telegram_id, first_name="Master")


async def test_apply_languages_surface_on_profile(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Languages sent on apply are exposed on GET /masters/me."""
    master = await _make_verified_master(
        client, db_session, languages=["Русский", "English"]
    )
    resp = await client.get(ME_URL, headers=auth_headers(master["session_token"]))
    assert resp.status_code == 200
    assert resp.json()["languages"] == ["Русский", "English"]


async def test_languages_default_empty(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Omitting languages on apply yields an empty list, not an error."""
    master = await _make_verified_master(client, db_session, languages=None)
    resp = await client.get(ME_URL, headers=auth_headers(master["session_token"]))
    body = resp.json()
    assert "languages" in body
    assert body["languages"] == []


async def test_patch_languages_replaces_set(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """PATCH /masters/me/languages replaces the set (freely, no moderation)."""
    master = await _make_verified_master(
        client, db_session, languages=["Русский"]
    )
    headers = auth_headers(master["session_token"])

    resp = await client.patch(
        LANGUAGES_URL, json={"languages": ["Русский", "English"]}, headers=headers
    )
    assert resp.status_code == 200
    assert resp.json()["languages"] == ["Русский", "English"]

    me = await client.get(ME_URL, headers=headers)
    assert me.json()["languages"] == ["Русский", "English"]


async def test_patch_languages_empty_clears(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """An empty list clears the language set."""
    master = await _make_verified_master(
        client, db_session, languages=["Русский", "English"]
    )
    headers = auth_headers(master["session_token"])

    resp = await client.patch(LANGUAGES_URL, json={"languages": []}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["languages"] == []


async def test_patch_languages_over_cap_rejected(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """More than 10 languages is rejected by validation (422)."""
    master = await _make_verified_master(client, db_session)
    resp = await client.patch(
        LANGUAGES_URL,
        json={"languages": [f"L{i}" for i in range(11)]},
        headers=auth_headers(master["session_token"]),
    )
    assert resp.status_code == 422
