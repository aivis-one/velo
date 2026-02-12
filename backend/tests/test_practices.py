# =============================================================================
# Test: Practices -- Master CRUD endpoints (Phase 4.2)
# =============================================================================
#
# telegram_id ranges:
#   60001-60099 -- master users
#   60100-60199 -- regular users (non-master)
#   60900-60999 -- admin users
# =============================================================================

from collections.abc import AsyncGenerator
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers import auth_headers, login_user

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
PRACTICES_URL = "/api/v1/practices"
MY_PRACTICES_URL = "/api/v1/masters/me/practices"
APPLY_URL = "/api/v1/masters/apply"
VERIFY_URL = "/api/v1/admin/masters/{user_id}/verify"

_CLEANUP_PRACTICES_SQL = text(
    "DELETE FROM practices WHERE master_id IN "
    "(SELECT user_id FROM master_profiles WHERE user_id IN "
    "(SELECT id FROM users WHERE telegram_id BETWEEN 60000 AND 60999))"
)
_CLEANUP_MASTERS_SQL = text(
    "DELETE FROM master_profiles WHERE user_id IN "
    "(SELECT id FROM users WHERE telegram_id BETWEEN 60000 AND 60999)"
)
_RESET_ROLES_SQL = text(
    "UPDATE users SET role = 'user' "
    "WHERE telegram_id BETWEEN 60000 AND 60999"
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
async def cleanup(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    """Clean practices, masters, and reset roles for test range."""
    await db_session.execute(_CLEANUP_PRACTICES_SQL)
    await db_session.execute(_CLEANUP_MASTERS_SQL)
    await db_session.execute(_RESET_ROLES_SQL)
    await db_session.commit()
    yield
    await db_session.execute(_CLEANUP_PRACTICES_SQL)
    await db_session.execute(_CLEANUP_MASTERS_SQL)
    await db_session.execute(_RESET_ROLES_SQL)
    await db_session.commit()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _valid_practice_body(**overrides: object) -> dict:
    """Return a valid CreatePracticeRequest body."""
    base = {
        "practice_type": "live",
        "title": "Morning Meditation",
        "description": "Guided breathwork session",
        "scheduled_at": (
            datetime.now(timezone.utc) + timedelta(days=7)
        ).isoformat(),
        "duration_minutes": 60,
        "timezone": "Europe/Moscow",
        "max_participants": 20,
    }
    base.update(overrides)
    return base


def _valid_apply_body() -> dict:
    """Return a valid MasterApplyRequest body."""
    return {
        "profile": {
            "display_name": "Test Master",
            "email": "master@test.com",
        },
        "experience": {
            "methods": ["meditation"],
            "experience_years": 5,
            "bio": "Experienced practitioner",
        },
        "documents": [],
    }


async def _make_verified_master(
    client: AsyncClient,
    db_session: AsyncSession,
    telegram_id: int = 60001,
) -> dict:
    """Create a user, apply as master, verify via admin. Returns auth data."""
    # Create user and apply.
    auth = await login_user(
        client, telegram_id=telegram_id, first_name="Master"
    )
    await client.post(
        APPLY_URL,
        json=_valid_apply_body(),
        headers=auth_headers(auth["session_token"]),
    )

    # Create admin and verify.
    admin_auth = await login_user(
        client, telegram_id=60900, first_name="Admin"
    )
    # Set admin role directly in DB.
    await db_session.execute(
        text(
            "UPDATE users SET role = 'admin' "
            "WHERE telegram_id = 60900"
        )
    )
    await db_session.commit()

    # Re-login admin to pick up new role in session.
    admin_auth = await login_user(
        client, telegram_id=60900, first_name="Admin"
    )

    user_id = auth["user"]["id"]
    verify_resp = await client.post(
        VERIFY_URL.format(user_id=user_id),
        json={},
        headers=auth_headers(admin_auth["session_token"]),
    )
    assert verify_resp.status_code == 200

    # Re-login to get updated role in session.
    auth = await login_user(
        client, telegram_id=telegram_id, first_name="Master"
    )
    return auth


# ---------------------------------------------------------------------------
# POST /practices -- success
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_create_practice_success(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Verified master can create a practice."""
    auth = await _make_verified_master(client, db_session)

    resp = await client.post(
        PRACTICES_URL,
        json=_valid_practice_body(),
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["practice_type"] == "live"
    assert data["title"] == "Morning Meditation"
    assert data["status"] == "draft"
    assert data["master_id"] == auth["user"]["id"]


# ---------------------------------------------------------------------------
# POST /practices -- not master (403)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_create_practice_not_master(
    client: AsyncClient,
) -> None:
    """Regular user cannot create a practice: 403."""
    auth = await login_user(
        client, telegram_id=60100, first_name="RegularUser"
    )

    resp = await client.post(
        PRACTICES_URL,
        json=_valid_practice_body(),
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# POST /practices -- no auth (401)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_create_practice_no_auth(client: AsyncClient) -> None:
    """No Authorization header: 401."""
    resp = await client.post(
        PRACTICES_URL,
        json=_valid_practice_body(),
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# POST /practices -- scheduled_at in past (422)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_create_practice_past_scheduled_at(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """scheduled_at in the past: 422."""
    auth = await _make_verified_master(client, db_session)

    body = _valid_practice_body(
        scheduled_at=(
            datetime.now(timezone.utc) - timedelta(hours=1)
        ).isoformat()
    )
    resp = await client.post(
        PRACTICES_URL,
        json=body,
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# POST /practices -- invalid timezone (422)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_create_practice_invalid_timezone(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Invalid IANA timezone: 422."""
    auth = await _make_verified_master(client, db_session)

    body = _valid_practice_body(timezone="Mars/Olympus")
    resp = await client.post(
        PRACTICES_URL,
        json=body,
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# POST /practices -- duration out of range (422)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_create_practice_duration_out_of_range(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """duration_minutes outside config bounds: 422."""
    auth = await _make_verified_master(client, db_session)

    body = _valid_practice_body(duration_minutes=9999)
    resp = await client.post(
        PRACTICES_URL,
        json=body,
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /practices/{id} -- success
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_get_practice_success(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Any authenticated user can view a scheduled practice."""
    master_auth = await _make_verified_master(client, db_session)

    # Create and set to scheduled.
    create_resp = await client.post(
        PRACTICES_URL,
        json=_valid_practice_body(),
        headers=auth_headers(master_auth["session_token"]),
    )
    assert create_resp.status_code == 201
    practice_id = create_resp.json()["id"]

    # Update status to scheduled.
    await client.patch(
        f"{PRACTICES_URL}/{practice_id}",
        json={"status": "scheduled"},
        headers=auth_headers(master_auth["session_token"]),
    )

    # Regular user can see it.
    user_auth = await login_user(
        client, telegram_id=60101, first_name="Viewer"
    )
    resp = await client.get(
        f"{PRACTICES_URL}/{practice_id}",
        headers=auth_headers(user_auth["session_token"]),
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == practice_id


# ---------------------------------------------------------------------------
# GET /practices/{id} -- draft visible to owner
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_get_draft_practice_owner(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Master can see their own draft practice."""
    auth = await _make_verified_master(client, db_session)

    create_resp = await client.post(
        PRACTICES_URL,
        json=_valid_practice_body(),
        headers=auth_headers(auth["session_token"]),
    )
    assert create_resp.status_code == 201
    practice_id = create_resp.json()["id"]

    resp = await client.get(
        f"{PRACTICES_URL}/{practice_id}",
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "draft"


# ---------------------------------------------------------------------------
# GET /practices/{id} -- draft not visible to others (404)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_get_draft_practice_not_owner(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Non-owner cannot see a draft practice: 404."""
    master_auth = await _make_verified_master(client, db_session)

    create_resp = await client.post(
        PRACTICES_URL,
        json=_valid_practice_body(),
        headers=auth_headers(master_auth["session_token"]),
    )
    assert create_resp.status_code == 201
    practice_id = create_resp.json()["id"]

    user_auth = await login_user(
        client, telegram_id=60102, first_name="Stranger"
    )
    resp = await client.get(
        f"{PRACTICES_URL}/{practice_id}",
        headers=auth_headers(user_auth["session_token"]),
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# PATCH /practices/{id} -- success
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_update_practice_success(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Master can update their own practice."""
    auth = await _make_verified_master(client, db_session)

    create_resp = await client.post(
        PRACTICES_URL,
        json=_valid_practice_body(),
        headers=auth_headers(auth["session_token"]),
    )
    assert create_resp.status_code == 201
    practice_id = create_resp.json()["id"]

    resp = await client.patch(
        f"{PRACTICES_URL}/{practice_id}",
        json={"title": "Evening Yoga"},
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Evening Yoga"


# ---------------------------------------------------------------------------
# PATCH /practices/{id} -- not owner (403)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_update_practice_not_owner(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Non-owner master cannot update practice: 403."""
    master_auth = await _make_verified_master(
        client, db_session, telegram_id=60002
    )

    create_resp = await client.post(
        PRACTICES_URL,
        json=_valid_practice_body(),
        headers=auth_headers(master_auth["session_token"]),
    )
    assert create_resp.status_code == 201
    practice_id = create_resp.json()["id"]

    # Create another master.
    other_auth = await _make_verified_master(
        client, db_session, telegram_id=60003
    )

    resp = await client.patch(
        f"{PRACTICES_URL}/{practice_id}",
        json={"title": "Hijacked"},
        headers=auth_headers(other_auth["session_token"]),
    )
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# DELETE /practices/{id} -- draft success
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_delete_draft_practice(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Master can delete a draft practice (status -> deleted)."""
    auth = await _make_verified_master(client, db_session)

    create_resp = await client.post(
        PRACTICES_URL,
        json=_valid_practice_body(),
        headers=auth_headers(auth["session_token"]),
    )
    assert create_resp.status_code == 201
    practice_id = create_resp.json()["id"]

    resp = await client.delete(
        f"{PRACTICES_URL}/{practice_id}",
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "deleted"


# ---------------------------------------------------------------------------
# DELETE /practices/{id} -- non-draft (400)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_delete_non_draft_practice(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Cannot delete a scheduled practice: 400."""
    auth = await _make_verified_master(client, db_session)

    create_resp = await client.post(
        PRACTICES_URL,
        json=_valid_practice_body(),
        headers=auth_headers(auth["session_token"]),
    )
    assert create_resp.status_code == 201
    practice_id = create_resp.json()["id"]

    # Set to scheduled.
    await client.patch(
        f"{PRACTICES_URL}/{practice_id}",
        json={"status": "scheduled"},
        headers=auth_headers(auth["session_token"]),
    )

    resp = await client.delete(
        f"{PRACTICES_URL}/{practice_id}",
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# PATCH /practices/{id} -- invalid status transition (400)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_update_practice_invalid_transition(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Cannot transition from draft to completed: 400."""
    auth = await _make_verified_master(client, db_session)

    create_resp = await client.post(
        PRACTICES_URL,
        json=_valid_practice_body(),
        headers=auth_headers(auth["session_token"]),
    )
    assert create_resp.status_code == 201
    practice_id = create_resp.json()["id"]

    resp = await client.patch(
        f"{PRACTICES_URL}/{practice_id}",
        json={"status": "completed"},
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# PATCH /practices/{id} -- null NOT NULL field (400, P-02)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_update_practice_null_not_null_field(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Setting NOT NULL field to null: 400."""
    auth = await _make_verified_master(client, db_session)

    create_resp = await client.post(
        PRACTICES_URL,
        json=_valid_practice_body(),
        headers=auth_headers(auth["session_token"]),
    )
    assert create_resp.status_code == 201
    practice_id = create_resp.json()["id"]

    resp = await client.patch(
        f"{PRACTICES_URL}/{practice_id}",
        json={"scheduled_at": None},
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# GET /masters/me/practices -- success
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_list_my_practices(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Master can list their own practices."""
    auth = await _make_verified_master(client, db_session)

    # Create 2 practices.
    for title in ("Practice A", "Practice B"):
        resp = await client.post(
            PRACTICES_URL,
            json=_valid_practice_body(title=title),
            headers=auth_headers(auth["session_token"]),
        )
        assert resp.status_code == 201

    resp = await client.get(
        MY_PRACTICES_URL,
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert all(
        p["master_id"] == auth["user"]["id"] for p in data
    )
