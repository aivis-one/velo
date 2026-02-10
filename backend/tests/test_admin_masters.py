# =============================================================================
# Test: Admin -- Master verification and rejection (Phase 2.3)
# =============================================================================
#
# telegram_id ranges:
#   56001-56099 -- master applicants
#   56900-56999 -- admin users
# =============================================================================

from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import text, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.masters.models import MasterProfile
from app.modules.users.models import User, UserRole
from tests.helpers import auth_headers, login_user


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
VERIFY_URL = "/api/v1/admin/masters/{user_id}/verify"
REJECT_URL = "/api/v1/admin/masters/{user_id}/reject"
APPLY_URL = "/api/v1/masters/apply"

_CLEANUP_SQL = text(
    "DELETE FROM master_profiles WHERE user_id IN "
    "(SELECT id FROM users WHERE telegram_id BETWEEN 56000 AND 56999)"
)

_RESET_ROLES_SQL = text(
    "UPDATE users SET role = 'user' "
    "WHERE telegram_id BETWEEN 56000 AND 56999 AND role != 'user'"
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
            "display_name": "Verify Test Master",
            "email": "verify@test.com",
            "phone": "+1234567890",
        },
        "experience": {
            "methods": ["meditation"],
            "experience_years": 5,
            "bio": "Test master for admin verification",
            "certifications": ["Cert A"],
        },
        "documents": [{"type": "certificate", "number": "CERT-001"}],
    }


async def _create_applicant(
    client: AsyncClient,
    telegram_id: int,
    first_name: str = "Applicant",
) -> tuple[dict, str]:
    """Create a user and submit a master application. Returns (auth_data, token)."""
    auth = await login_user(
        client, telegram_id=telegram_id, first_name=first_name
    )
    token = auth["session_token"]

    resp = await client.post(
        APPLY_URL,
        json=_valid_apply_body(),
        headers=auth_headers(token),
    )
    assert resp.status_code == 201
    return auth, token


async def _make_admin(
    client: AsyncClient,
    db_session: AsyncSession,
    telegram_id: int = 56900,
    first_name: str = "Admin",
) -> tuple[dict, str]:
    """Create a user and upgrade to admin role. Returns (auth_data, token)."""
    auth = await login_user(
        client, telegram_id=telegram_id, first_name=first_name
    )
    token = auth["session_token"]
    user_id = auth["user"]["id"]

    await db_session.execute(
        update(User)
        .where(User.id == user_id)
        .values(role=UserRole.ADMIN.value)
    )
    await db_session.commit()

    return auth, token


# ---------------------------------------------------------------------------
# POST /admin/masters/{user_id}/verify -- success
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_verify_master_success(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Admin verifies pending application: status=verified, role=master."""
    # Setup: applicant + admin.
    applicant_auth, _ = await _create_applicant(client, telegram_id=56001)
    _, admin_token = await _make_admin(client, db_session)

    user_id = applicant_auth["user"]["id"]
    url = VERIFY_URL.format(user_id=user_id)

    # Act.
    resp = await client.post(
        url,
        json={"notes": "All documents OK"},
        headers=auth_headers(admin_token),
    )

    # Assert response.
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "verified"
    assert data["user_id"] == user_id

    # Assert DB: profile status.
    profile = await db_session.get(MasterProfile, user_id)
    await db_session.refresh(profile)
    assert profile.data["account"]["status"] == "verified"
    assert profile.data["account"]["verification"]["notes"] == "All documents OK"

    # Assert DB: user role upgraded to MASTER.
    user = await db_session.get(User, user_id)
    await db_session.refresh(user)
    assert user.role == UserRole.MASTER


# ---------------------------------------------------------------------------
# POST /admin/masters/{user_id}/verify -- no notes (optional)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_verify_master_no_notes(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Verify without notes: success, notes=null in JSONB."""
    applicant_auth, _ = await _create_applicant(client, telegram_id=56002)
    _, admin_token = await _make_admin(client, db_session, telegram_id=56901)

    user_id = applicant_auth["user"]["id"]
    url = VERIFY_URL.format(user_id=user_id)

    resp = await client.post(
        url,
        json={},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 200

    profile = await db_session.get(MasterProfile, user_id)
    await db_session.refresh(profile)
    assert profile.data["account"]["verification"]["notes"] is None


# ---------------------------------------------------------------------------
# POST /admin/masters/{user_id}/reject -- success
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_reject_master_success(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Admin rejects pending application: status=rejected, role stays USER."""
    applicant_auth, _ = await _create_applicant(client, telegram_id=56003)
    _, admin_token = await _make_admin(client, db_session, telegram_id=56902)

    user_id = applicant_auth["user"]["id"]
    url = REJECT_URL.format(user_id=user_id)

    resp = await client.post(
        url,
        json={"reason": "Insufficient experience"},
        headers=auth_headers(admin_token),
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "rejected"
    assert data["user_id"] == user_id

    # Assert DB: profile status.
    profile = await db_session.get(MasterProfile, user_id)
    await db_session.refresh(profile)
    assert profile.data["account"]["status"] == "rejected"
    assert profile.data["account"]["rejection_reason"] == "Insufficient experience"

    # Assert DB: user role NOT changed.
    user = await db_session.get(User, user_id)
    await db_session.refresh(user)
    assert user.role == UserRole.USER


# ---------------------------------------------------------------------------
# POST /admin/masters/{user_id}/verify -- no auth
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_verify_no_auth(client: AsyncClient) -> None:
    """No Authorization header: 401."""
    url = VERIFY_URL.format(user_id=uuid4())
    resp = await client.post(url, json={})
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# POST /admin/masters/{user_id}/verify -- non-admin
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_verify_non_admin(client: AsyncClient) -> None:
    """Regular user (not admin): 403."""
    auth = await login_user(client, telegram_id=56010, first_name="NotAdmin")
    url = VERIFY_URL.format(user_id=uuid4())

    resp = await client.post(
        url,
        json={},
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# POST /admin/masters/{user_id}/verify -- not found
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_verify_nonexistent_user(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Non-existent user_id: 404."""
    _, admin_token = await _make_admin(client, db_session, telegram_id=56903)

    url = VERIFY_URL.format(user_id=uuid4())
    resp = await client.post(
        url,
        json={},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# POST /admin/masters/{user_id}/verify -- already verified
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_verify_already_verified(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Verifying an already-verified master: 409."""
    applicant_auth, _ = await _create_applicant(client, telegram_id=56004)
    _, admin_token = await _make_admin(client, db_session, telegram_id=56904)

    user_id = applicant_auth["user"]["id"]
    url = VERIFY_URL.format(user_id=user_id)

    # First verify -- success.
    resp1 = await client.post(url, json={}, headers=auth_headers(admin_token))
    assert resp1.status_code == 200

    # Second verify -- conflict.
    resp2 = await client.post(url, json={}, headers=auth_headers(admin_token))
    assert resp2.status_code == 409


# ---------------------------------------------------------------------------
# POST /admin/masters/{user_id}/verify -- rejected profile
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_verify_rejected_profile(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Cannot verify a rejected application (must reapply first): 409."""
    applicant_auth, _ = await _create_applicant(client, telegram_id=56005)
    _, admin_token = await _make_admin(client, db_session, telegram_id=56905)

    user_id = applicant_auth["user"]["id"]

    # Reject first.
    reject_url = REJECT_URL.format(user_id=user_id)
    resp1 = await client.post(
        reject_url,
        json={"reason": "Not ready"},
        headers=auth_headers(admin_token),
    )
    assert resp1.status_code == 200

    # Try to verify the rejected profile.
    verify_url = VERIFY_URL.format(user_id=user_id)
    resp2 = await client.post(
        verify_url, json={}, headers=auth_headers(admin_token)
    )
    assert resp2.status_code == 409


# ---------------------------------------------------------------------------
# POST /admin/masters/{user_id}/reject -- empty reason
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_reject_empty_reason(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Rejection without reason: 422 validation error."""
    _, admin_token = await _make_admin(client, db_session, telegram_id=56906)

    url = REJECT_URL.format(user_id=uuid4())
    resp = await client.post(
        url,
        json={"reason": ""},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Integration: reject -> reapply -> verify (full cycle)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_reject_reapply_verify_cycle(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Full lifecycle: apply -> reject -> reapply -> verify."""
    applicant_auth, applicant_token = await _create_applicant(
        client, telegram_id=56006
    )
    _, admin_token = await _make_admin(client, db_session, telegram_id=56907)
    user_id = applicant_auth["user"]["id"]

    # Step 1: Admin rejects.
    reject_url = REJECT_URL.format(user_id=user_id)
    resp1 = await client.post(
        reject_url,
        json={"reason": "Need more experience"},
        headers=auth_headers(admin_token),
    )
    assert resp1.status_code == 200

    # Step 2: User reapplies.
    new_body = _valid_apply_body()
    new_body["experience"]["experience_years"] = 10
    resp2 = await client.post(
        APPLY_URL,
        json=new_body,
        headers=auth_headers(applicant_token),
    )
    assert resp2.status_code == 201
    assert resp2.json()["status"] == "pending"

    # Step 3: Admin verifies.
    verify_url = VERIFY_URL.format(user_id=user_id)
    resp3 = await client.post(
        verify_url,
        json={"notes": "Improved application"},
        headers=auth_headers(admin_token),
    )
    assert resp3.status_code == 200
    assert resp3.json()["status"] == "verified"

    # Assert: rejection history preserved.
    profile = await db_session.get(MasterProfile, user_id)
    await db_session.refresh(profile)
    rejections = profile.data["account"].get("rejections", [])
    assert len(rejections) == 1
    assert rejections[0]["reason"] == "Need more experience"

    # Assert: user is now MASTER.
    user = await db_session.get(User, user_id)
    await db_session.refresh(user)
    assert user.role == UserRole.MASTER
