# =============================================================================
# Test: Masters Module — application flow
# =============================================================================

from collections.abc import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy import select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.masters.models import MasterProfile
from app.modules.users.models import User, UserRole
from tests.helpers import auth_headers, login_user


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

APPLY_URL = "/api/v1/masters/apply"


@pytest.fixture(autouse=True)
async def cleanup_test_masters(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    """Remove master_profiles for test users (55xxx) after each test."""
    yield
    await db_session.execute(
        text(
            "DELETE FROM master_profiles WHERE user_id IN "
            "(SELECT id FROM users WHERE telegram_id BETWEEN 55000 AND 55999)"
        )
    )
    await db_session.commit()


def _valid_apply_body() -> dict:
    """Minimal valid application payload."""
    return {
        "profile": {
            "display_name": "Test Master",
            "email": "master@test.com",
            "phone": "+1234567890",
        },
        "experience": {
            "methods": ["meditation"],
            "experience_years": 3,
            "bio": "Experienced meditation teacher",
            "certifications": ["Cert A"],
        },
        "documents": [
            {"type": "certificate", "number": "ABC-123"},
        ],
    }


# ---------------------------------------------------------------------------
# POST /masters/apply — success
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_apply_master_success(client: AsyncClient) -> None:
    """User can submit a master application."""
    auth = await login_user(client, telegram_id=55001, first_name="Applicant")
    token = auth["session_token"]

    response = await client.post(
        APPLY_URL,
        json=_valid_apply_body(),
        headers=auth_headers(token),
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"
    assert data["user_id"] == auth["user"]["id"]


# ---------------------------------------------------------------------------
# POST /masters/apply — duplicate (already pending)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_apply_master_already_pending(client: AsyncClient) -> None:
    """Second application while pending → 409 Conflict."""
    auth = await login_user(client, telegram_id=55002, first_name="Duplicate")
    token = auth["session_token"]

    # First application.
    resp1 = await client.post(
        APPLY_URL,
        json=_valid_apply_body(),
        headers=auth_headers(token),
    )
    assert resp1.status_code == 201

    # Second application — should fail.
    resp2 = await client.post(
        APPLY_URL,
        json=_valid_apply_body(),
        headers=auth_headers(token),
    )
    assert resp2.status_code == 409


# ---------------------------------------------------------------------------
# POST /masters/apply — reapply after rejection
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_apply_master_reapply_after_rejection(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Rejected user can reapply — profile is updated, not duplicated."""
    auth = await login_user(client, telegram_id=55003, first_name="Rejected")
    token = auth["session_token"]

    # First application.
    resp1 = await client.post(
        APPLY_URL,
        json=_valid_apply_body(),
        headers=auth_headers(token),
    )
    assert resp1.status_code == 201

    # Simulate admin rejection by updating JSONB directly.
    user_id = auth["user"]["id"]
    stmt = select(MasterProfile).where(
        MasterProfile.user_id == user_id
    )
    result = await db_session.execute(stmt)
    profile = result.scalar_one()

    data = dict(profile.data)
    data["account"]["status"] = "rejected"
    data["account"]["rejected_at"] = "2026-02-09T00:00:00Z"
    data["account"]["rejection_reason"] = "Not enough experience"
    profile.data = data
    await db_session.commit()

    # Reapply with updated info.
    new_body = _valid_apply_body()
    new_body["experience"]["experience_years"] = 10
    new_body["experience"]["bio"] = "Now with more experience"

    resp2 = await client.post(
        APPLY_URL,
        json=new_body,
        headers=auth_headers(token),
    )
    assert resp2.status_code == 201
    assert resp2.json()["status"] == "pending"

    # Verify rejection history is preserved.
    await db_session.refresh(profile)
    rejections = profile.data["account"]["rejections"]
    assert len(rejections) == 1
    assert rejections[0]["reason"] == "Not enough experience"


# ---------------------------------------------------------------------------
# POST /masters/apply — no auth
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_apply_master_no_auth(client: AsyncClient) -> None:
    """Unauthenticated request → 401."""
    response = await client.post(APPLY_URL, json=_valid_apply_body())
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# POST /masters/apply — master role forbidden
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_apply_master_already_master(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """User with role=master cannot reapply → 403."""
    auth = await login_user(client, telegram_id=55004, first_name="AlreadyMaster")
    token = auth["session_token"]

    # Upgrade role to MASTER directly in DB.
    user_id = auth["user"]["id"]
    await db_session.execute(
        update(User).where(User.id == user_id).values(role=UserRole.MASTER.value)
    )
    await db_session.commit()

    response = await client.post(
        APPLY_URL,
        json=_valid_apply_body(),
        headers=auth_headers(token),
    )
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# POST /masters/apply — validation errors
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_apply_master_missing_methods(client: AsyncClient) -> None:
    """Empty methods list → 422."""
    auth = await login_user(client, telegram_id=55005, first_name="NoMethods")
    token = auth["session_token"]

    body = _valid_apply_body()
    body["experience"]["methods"] = []

    response = await client.post(
        APPLY_URL,
        json=body,
        headers=auth_headers(token),
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_apply_master_missing_display_name(client: AsyncClient) -> None:
    """Empty display_name → 422."""
    auth = await login_user(client, telegram_id=55006, first_name="NoName")
    token = auth["session_token"]

    body = _valid_apply_body()
    body["profile"]["display_name"] = ""

    response = await client.post(
        APPLY_URL,
        json=body,
        headers=auth_headers(token),
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_apply_master_negative_experience(client: AsyncClient) -> None:
    """Negative experience_years → 422."""
    auth = await login_user(client, telegram_id=55007, first_name="NegExp")
    token = auth["session_token"]

    body = _valid_apply_body()
    body["experience"]["experience_years"] = -1

    response = await client.post(
        APPLY_URL,
        json=body,
        headers=auth_headers(token),
    )
    assert response.status_code == 422
