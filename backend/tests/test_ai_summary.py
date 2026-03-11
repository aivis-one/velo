# =============================================================================
# Test: AI Summary Mock Endpoint (Phase 9.1)
# =============================================================================
#
# GET /api/v1/practices/{id}/ai-summary
#
# telegram_id ranges:
#   89001-89099 -- regular users
#   89100-89199 -- master users
# =============================================================================

from collections.abc import AsyncGenerator
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.masters.models import MasterProfile
from app.modules.practices.models import Practice, PracticeStatus, PracticeType
from app.modules.users.models import User, UserRole
from tests.helpers import auth_headers, login_user

UTC = timezone.utc
AI_SUMMARY_URL = "/api/v1/practices/{practice_id}/ai-summary"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
async def cleanup(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    """Clean test data before and after each test."""
    await _do_cleanup(db_session)
    yield
    await _do_cleanup(db_session)


async def _do_cleanup(session: AsyncSession) -> None:
    """ORM cleanup for telegram_id 89000-89999."""
    from tests.helpers import full_cleanup_range
    await full_cleanup_range(session, 89000, 89999, delete_users=False)
    await session.commit()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
async def _make_verified_master(
    client: AsyncClient,
    db_session: AsyncSession,
    telegram_id: int,
) -> dict:
    """Create a verified master and return auth dict."""
    auth = await login_user(client, telegram_id=telegram_id, first_name="Master")
    user_id = auth["user"]["id"]

    await db_session.execute(
        update(User)
        .where(User.id == user_id)
        .values(role=UserRole.MASTER.value)
    )

    profile = MasterProfile(
        user_id=user_id,
        data={
            "account": {"status": "verified"},
            "profile": {"bio": "Test bio", "methods": []},
        },
    )
    db_session.add(profile)
    await db_session.commit()
    return auth


async def _create_practice(
    db_session: AsyncSession,
    master_id: str,
    status: str = PracticeStatus.COMPLETED.value,
) -> Practice:
    """Create a practice with the given status."""
    practice = Practice(
        master_id=master_id,
        title="Test Practice",
        description="Description",
        practice_type=PracticeType.LIVE.value,
        status=status,
        scheduled_at=datetime.now(UTC) - timedelta(hours=2),
        duration_minutes=60,
        timezone="UTC",
        max_participants=20,
        current_participants=0,
        is_free=True,
        price_cents=0,
        currency="eur",
    )
    db_session.add(practice)
    await db_session.flush()
    return practice


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_ai_summary_success(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Owner master receives a placeholder summary (is_mock=True)."""
    master_auth = await _make_verified_master(client, db_session, telegram_id=89100)
    practice = await _create_practice(db_session, master_auth["user"]["id"])
    await db_session.commit()

    url = AI_SUMMARY_URL.format(practice_id=practice.id)
    resp = await client.get(url, headers=auth_headers(master_auth["session_token"]))

    assert resp.status_code == 200
    data = resp.json()

    assert data["practice_id"] == str(practice.id)
    assert isinstance(data["summary"], str)
    assert len(data["summary"]) > 0
    assert data["is_mock"] is True
    assert "generated_at" in data


@pytest.mark.asyncio
async def test_ai_summary_non_owner_gets_404(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Another master requesting someone else's practice: 404 (P-08)."""
    owner_auth = await _make_verified_master(client, db_session, telegram_id=89101)
    other_auth = await _make_verified_master(client, db_session, telegram_id=89102)
    practice = await _create_practice(db_session, owner_auth["user"]["id"])
    await db_session.commit()

    url = AI_SUMMARY_URL.format(practice_id=practice.id)
    resp = await client.get(url, headers=auth_headers(other_auth["session_token"]))

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_ai_summary_regular_user_gets_404(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Regular user (not the master) requesting a practice: 404 (P-08)."""
    master_auth = await _make_verified_master(client, db_session, telegram_id=89103)
    user_auth = await login_user(client, telegram_id=89001, first_name="User")
    practice = await _create_practice(db_session, master_auth["user"]["id"])
    await db_session.commit()

    url = AI_SUMMARY_URL.format(practice_id=practice.id)
    resp = await client.get(url, headers=auth_headers(user_auth["session_token"]))

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_ai_summary_practice_not_found(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Non-existent practice UUID: 404."""
    master_auth = await _make_verified_master(client, db_session, telegram_id=89104)

    url = AI_SUMMARY_URL.format(practice_id=uuid4())
    resp = await client.get(url, headers=auth_headers(master_auth["session_token"]))

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_ai_summary_no_auth(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """No Authorization header: 401."""
    master_auth = await _make_verified_master(client, db_session, telegram_id=89105)
    practice = await _create_practice(db_session, master_auth["user"]["id"])
    await db_session.commit()

    url = AI_SUMMARY_URL.format(practice_id=practice.id)
    resp = await client.get(url)

    assert resp.status_code == 401
