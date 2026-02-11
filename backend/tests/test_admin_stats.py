# =============================================================================
# Test: Admin -- Platform statistics (Phase 3.1)
# =============================================================================
#
# telegram_id ranges:
#   57001-57099 -- regular users for stats
#   57900-57999 -- admin users
# =============================================================================

from collections.abc import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy import text, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import User, UserRole
from tests.helpers import auth_headers, login_user

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
STATS_URL = "/api/v1/admin/stats"
APPLY_URL = "/api/v1/masters/apply"

_CLEANUP_SQL = text(
    "DELETE FROM master_profiles WHERE user_id IN "
    "(SELECT id FROM users WHERE telegram_id BETWEEN 57000 AND 57999)"
)

_RESET_ROLES_SQL = text(
    "UPDATE users SET role = 'user' "
    "WHERE telegram_id BETWEEN 57000 AND 57999 AND role != 'user'"
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
async def cleanup(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    """Clean master_profiles and reset roles for test range before/after."""
    await db_session.execute(_CLEANUP_SQL)
    await db_session.execute(_RESET_ROLES_SQL)
    await db_session.commit()
    yield
    await db_session.execute(_CLEANUP_SQL)
    await db_session.execute(_RESET_ROLES_SQL)
    await db_session.commit()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _valid_apply_body() -> dict:
    """Minimal valid master application payload."""
    return {
        "profile": {
            "display_name": "Stats Test Master",
            "email": "stats@test.com",
            "phone": "+1234567890",
        },
        "experience": {
            "methods": ["meditation"],
            "experience_years": 5,
            "bio": "Test master for stats",
            "certifications": ["Cert A"],
        },
        "documents": [{"type": "certificate", "number": "CERT-001"}],
    }


async def _make_admin(
    client: AsyncClient,
    db_session: AsyncSession,
    telegram_id: int = 57900,
) -> str:
    """Create admin user, return token."""
    auth = await login_user(
        client, telegram_id=telegram_id, first_name="StatsAdmin"
    )
    token = auth["session_token"]
    user_id = auth["user"]["id"]

    await db_session.execute(
        update(User)
        .where(User.id == user_id)
        .values(role=UserRole.ADMIN.value)
    )
    await db_session.commit()

    return token


# ---------------------------------------------------------------------------
# GET /admin/stats -- no auth
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_stats_no_auth(client: AsyncClient) -> None:
    """No Authorization header: 401."""
    resp = await client.get(STATS_URL)
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# GET /admin/stats -- non-admin
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_stats_non_admin(client: AsyncClient) -> None:
    """Regular user (not admin): 403."""
    auth = await login_user(client, telegram_id=57010, first_name="NotAdmin")
    resp = await client.get(
        STATS_URL, headers=auth_headers(auth["session_token"])
    )
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# GET /admin/stats -- basic counts
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_stats_basic_counts(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Stats reflect actual user and master counts."""
    admin_token = await _make_admin(client, db_session)

    # Baseline: at least the admin user exists.
    resp1 = await client.get(
        STATS_URL, headers=auth_headers(admin_token)
    )
    assert resp1.status_code == 200
    data1 = resp1.json()
    baseline_users = data1["users_count"]
    baseline_masters = data1["masters_count"]

    # Create 2 regular users.
    await login_user(client, telegram_id=57001, first_name="User1")
    await login_user(client, telegram_id=57002, first_name="User2")

    resp2 = await client.get(
        STATS_URL, headers=auth_headers(admin_token)
    )
    data2 = resp2.json()
    assert data2["users_count"] == baseline_users + 2
    assert data2["masters_count"] == baseline_masters


# ---------------------------------------------------------------------------
# GET /admin/stats -- pending verifications
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_stats_pending_verifications(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Pending count reflects actual pending master applications."""
    admin_token = await _make_admin(client, db_session)

    # Baseline pending count.
    resp1 = await client.get(
        STATS_URL, headers=auth_headers(admin_token)
    )
    baseline_pending = resp1.json()["pending_verifications"]

    # Submit 2 master applications.
    for tg_id in (57020, 57021):
        auth = await login_user(
            client, telegram_id=tg_id, first_name=f"Applicant{tg_id}"
        )
        await client.post(
            APPLY_URL,
            json=_valid_apply_body(),
            headers=auth_headers(auth["session_token"]),
        )

    resp2 = await client.get(
        STATS_URL, headers=auth_headers(admin_token)
    )
    assert resp2.json()["pending_verifications"] == baseline_pending + 2


# ---------------------------------------------------------------------------
# GET /admin/stats -- masters count after verification
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_stats_masters_count_after_verify(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Verifying a master increases masters_count, decreases pending."""
    admin_token = await _make_admin(client, db_session)

    # Create applicant and submit application.
    applicant_auth = await login_user(
        client, telegram_id=57030, first_name="ToVerify"
    )
    await client.post(
        APPLY_URL,
        json=_valid_apply_body(),
        headers=auth_headers(applicant_auth["session_token"]),
    )

    # Stats before verification.
    resp1 = await client.get(
        STATS_URL, headers=auth_headers(admin_token)
    )
    before = resp1.json()

    # Verify the applicant.
    user_id = applicant_auth["user"]["id"]
    verify_resp = await client.post(
        f"/api/v1/admin/masters/{user_id}/verify",
        json={},
        headers=auth_headers(admin_token),
    )
    assert verify_resp.status_code == 200

    # Stats after verification.
    resp2 = await client.get(
        STATS_URL, headers=auth_headers(admin_token)
    )
    after = resp2.json()

    assert after["masters_count"] == before["masters_count"] + 1
    assert after["pending_verifications"] == before["pending_verifications"] - 1


# ---------------------------------------------------------------------------
# GET /admin/stats -- practices_count is stub
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_stats_practices_count_stub(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """practices_count is always 0 (stub until Phase 4)."""
    admin_token = await _make_admin(client, db_session, telegram_id=57901)

    resp = await client.get(
        STATS_URL, headers=auth_headers(admin_token)
    )
    assert resp.status_code == 200
    assert resp.json()["practices_count"] == 0
