# =============================================================================
# Test: Role Switch — TEST-ONLY tester tool (POST /api/v1/users/me/role)
# =============================================================================
#
# Covers the dedicated-flag gate, the per-user allow-list, the master-profile
# requirement, and the role_switch block surfaced in GET /users/me.
#
# The feature is OFF by default (settings.role_switch_enabled = False). Tests
# that exercise the enabled behaviour flip the singleton flag via monkeypatch;
# both the router and the UserResponse computed_field read the same settings
# object, so one patch covers both. Cleanup of the telegram_id range removes
# the MasterProfiles created here so they never leak into other suites.
# =============================================================================

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.masters.models import MasterProfile
from app.modules.users.models import User
from tests.helpers import auth_headers, full_cleanup_range, login_user

TID_MIN = 88200
TID_MAX = 88299


@pytest.fixture(autouse=True)
async def _cleanup(db_session: AsyncSession):
    """Wipe the role-switch telegram_id range before and after each test."""
    await full_cleanup_range(db_session, TID_MIN, TID_MAX)
    await db_session.commit()
    yield
    await full_cleanup_range(db_session, TID_MIN, TID_MAX)
    await db_session.commit()


async def _seed_role_switch(
    db_session: AsyncSession,
    telegram_id: int,
    allowed_roles: list[str],
    *,
    with_master_profile: bool = False,
) -> None:
    """Seed credentials.role_switch.allowed_roles for an existing user.

    Mirrors what seed_practices will write. Optionally attaches a verified
    MasterProfile so a switch into the master role is accepted.
    """
    user = (
        await db_session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
    ).scalar_one()

    creds = dict(user.credentials or {})
    creds["role_switch"] = {"allowed_roles": allowed_roles}
    user.set_jsonb("credentials", creds)

    if with_master_profile:
        profile = MasterProfile(user_id=user.id)
        profile.set_jsonb("data", {"account": {"status": "verified"}})
        db_session.add(profile)

    await db_session.commit()


# ---------------------------------------------------------------------------
# Gate: feature flag
# ---------------------------------------------------------------------------


async def test_switch_role_404_when_feature_disabled(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """With the flag off (default, i.e. production), the endpoint 404s."""
    # Force the flag OFF so the test does not depend on the ambient
    # ROLE_SWITCH_ENABLED env. Mirrors the enabled tests' monkeypatch.
    monkeypatch.setattr(settings, "role_switch_enabled", False)
    data = await login_user(client, telegram_id=88200, first_name="Off")
    token = data["session_token"]

    response = await client.post(
        "/api/v1/users/me/role",
        headers=auth_headers(token),
        json={"role": "admin"},
    )
    assert response.status_code == 404


async def test_switch_role_no_auth_401(client: AsyncClient) -> None:
    """No token → 401 (auth dependency runs before the handler)."""
    response = await client.post(
        "/api/v1/users/me/role",
        json={"role": "admin"},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Happy paths
# ---------------------------------------------------------------------------


async def test_switch_to_admin_success(
    client: AsyncClient,
    db_session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A tester allowed admin can switch; role flips and GET /me reflects it."""
    monkeypatch.setattr(settings, "role_switch_enabled", True)
    data = await login_user(client, telegram_id=88201, first_name="Admin")
    token = data["session_token"]
    await _seed_role_switch(db_session, 88201, ["user", "master", "admin"])

    response = await client.post(
        "/api/v1/users/me/role",
        headers=auth_headers(token),
        json={"role": "admin"},
    )
    assert response.status_code == 200
    assert response.json()["role"] == "admin"

    me = await client.get("/api/v1/users/me", headers=auth_headers(token))
    assert me.json()["role"] == "admin"


async def test_switch_to_master_with_profile_success(
    client: AsyncClient,
    db_session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Switch to master succeeds when a verified MasterProfile exists."""
    monkeypatch.setattr(settings, "role_switch_enabled", True)
    data = await login_user(client, telegram_id=88202, first_name="Master")
    token = data["session_token"]
    await _seed_role_switch(
        db_session, 88202, ["user", "master", "admin"], with_master_profile=True
    )

    response = await client.post(
        "/api/v1/users/me/role",
        headers=auth_headers(token),
        json={"role": "master"},
    )
    assert response.status_code == 200
    assert response.json()["role"] == "master"


async def test_switch_back_to_user_success(
    client: AsyncClient,
    db_session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A tester can return to the user role (round-trip)."""
    monkeypatch.setattr(settings, "role_switch_enabled", True)
    data = await login_user(client, telegram_id=88203, first_name="RoundTrip")
    token = data["session_token"]
    await _seed_role_switch(db_session, 88203, ["user", "master", "admin"])

    await client.post(
        "/api/v1/users/me/role",
        headers=auth_headers(token),
        json={"role": "admin"},
    )
    response = await client.post(
        "/api/v1/users/me/role",
        headers=auth_headers(token),
        json={"role": "user"},
    )
    assert response.status_code == 200
    assert response.json()["role"] == "user"


# ---------------------------------------------------------------------------
# Authorization & validation failures
# ---------------------------------------------------------------------------


async def test_switch_to_role_not_in_allowlist_403(
    client: AsyncClient,
    db_session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Requesting a role outside the seeded allow-list → 403."""
    monkeypatch.setattr(settings, "role_switch_enabled", True)
    data = await login_user(client, telegram_id=88204, first_name="Limited")
    token = data["session_token"]
    # Allowed only user — admin is off-limits.
    await _seed_role_switch(db_session, 88204, ["user"])

    response = await client.post(
        "/api/v1/users/me/role",
        headers=auth_headers(token),
        json={"role": "admin"},
    )
    assert response.status_code == 403
    assert response.json()["error"] == "role_not_allowed"


async def test_non_tester_cannot_switch_403(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A user with no seeded allow-list cannot switch even when flag is on."""
    monkeypatch.setattr(settings, "role_switch_enabled", True)
    data = await login_user(client, telegram_id=88205, first_name="Plain")
    token = data["session_token"]

    response = await client.post(
        "/api/v1/users/me/role",
        headers=auth_headers(token),
        json={"role": "master"},
    )
    assert response.status_code == 403


async def test_switch_to_master_without_profile_409(
    client: AsyncClient,
    db_session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Master is allowed but no verified profile exists → 409."""
    monkeypatch.setattr(settings, "role_switch_enabled", True)
    data = await login_user(client, telegram_id=88206, first_name="NoProfile")
    token = data["session_token"]
    await _seed_role_switch(db_session, 88206, ["user", "master", "admin"])

    response = await client.post(
        "/api/v1/users/me/role",
        headers=auth_headers(token),
        json={"role": "master"},
    )
    assert response.status_code == 409
    assert response.json()["error"] == "master_profile_required"


async def test_switch_invalid_role_422(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An unknown role value is rejected by Pydantic → 422."""
    monkeypatch.setattr(settings, "role_switch_enabled", True)
    data = await login_user(client, telegram_id=88207, first_name="Bogus")
    token = data["session_token"]

    response = await client.post(
        "/api/v1/users/me/role",
        headers=auth_headers(token),
        json={"role": "superuser"},
    )
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /users/me — role_switch block exposure
# ---------------------------------------------------------------------------


async def test_me_exposes_role_switch_when_enabled(
    client: AsyncClient,
    db_session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """With the flag on, a seeded tester sees their allowed_roles in /me."""
    monkeypatch.setattr(settings, "role_switch_enabled", True)
    data = await login_user(client, telegram_id=88208, first_name="Exposed")
    token = data["session_token"]
    await _seed_role_switch(db_session, 88208, ["user", "master", "admin"])

    me = await client.get("/api/v1/users/me", headers=auth_headers(token))
    assert me.status_code == 200
    assert me.json()["role_switch"] == {
        "allowed_roles": ["user", "master", "admin"]
    }


async def test_me_hides_role_switch_when_disabled(
    client: AsyncClient,
    db_session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """With the flag off, role_switch is null even for a seeded user."""
    # Force the flag OFF so the test does not depend on the ambient
    # ROLE_SWITCH_ENABLED env. Mirrors the enabled tests' monkeypatch.
    monkeypatch.setattr(settings, "role_switch_enabled", False)
    data = await login_user(client, telegram_id=88209, first_name="Hidden")
    token = data["session_token"]
    await _seed_role_switch(db_session, 88209, ["user", "master", "admin"])

    me = await client.get("/api/v1/users/me", headers=auth_headers(token))
    assert me.status_code == 200
    assert me.json()["role_switch"] is None


async def test_me_role_switch_null_for_non_tester(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Flag on, but a user with no allow-list gets role_switch null."""
    monkeypatch.setattr(settings, "role_switch_enabled", True)
    data = await login_user(client, telegram_id=88210, first_name="Nobody")
    token = data["session_token"]

    me = await client.get("/api/v1/users/me", headers=auth_headers(token))
    assert me.status_code == 200
    assert me.json()["role_switch"] is None
