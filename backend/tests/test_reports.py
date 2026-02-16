# =============================================================================
# Test: Reports -- User-facing report endpoints (Phase 3.3)
# =============================================================================
#
# telegram_id ranges:
#   59001-59099 -- regular users (reporters)
#   59100-59199 -- target users (reported)
#   59900-59999 -- admin users
# =============================================================================

from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers import auth_headers, login_user

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
REPORTS_URL = "/api/v1/reports"
REPORTS_ME_URL = "/api/v1/reports/me"

_CLEANUP_REPORTS_SQL = text(
    "DELETE FROM reports WHERE reporter_id IN "
    "(SELECT id FROM users WHERE telegram_id BETWEEN 59000 AND 59999)"
)

_DELETE_MASTERS_SQL = text(
    "DELETE FROM master_profiles WHERE user_id IN "
    "(SELECT id FROM users WHERE telegram_id BETWEEN 59000 AND 59999)"
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
async def cleanup(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    """Clean reports for test range before/after."""
    await db_session.execute(_CLEANUP_REPORTS_SQL)
    await db_session.execute(_DELETE_MASTERS_SQL)
    await db_session.commit()
    yield
    await db_session.execute(_CLEANUP_REPORTS_SQL)
    await db_session.execute(_DELETE_MASTERS_SQL)
    await db_session.commit()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
async def _create_target_user(
    client: AsyncClient,
    telegram_id: int = 59100,
) -> dict:
    """Create a user to be reported. Returns auth data."""
    return await login_user(client, telegram_id=telegram_id, first_name="Target")


# ---------------------------------------------------------------------------
# POST /reports -- success
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_create_report_success(client: AsyncClient) -> None:
    """User can create a report against another user."""
    reporter = await login_user(client, telegram_id=59001, first_name="Reporter")
    target = await _create_target_user(client, telegram_id=59100)

    resp = await client.post(
        REPORTS_URL,
        json={
            "target_type": "user",
            "target_id": target["user"]["id"],
            "reason": "Inappropriate behavior",
        },
        headers=auth_headers(reporter["session_token"]),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["target_type"] == "user"
    assert data["target_id"] == target["user"]["id"]
    assert data["reason"] == "Inappropriate behavior"
    assert data["status"] == "pending"
    assert data["reporter_id"] == reporter["user"]["id"]


# ---------------------------------------------------------------------------
# POST /reports -- no auth
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_create_report_no_auth(client: AsyncClient) -> None:
    """No Authorization header: 401."""
    resp = await client.post(
        REPORTS_URL,
        json={
            "target_type": "user",
            "target_id": str(uuid4()),
            "reason": "Test",
        },
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# POST /reports -- target not found
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_create_report_target_not_found(client: AsyncClient) -> None:
    """Report against non-existent user: 404."""
    reporter = await login_user(client, telegram_id=59002, first_name="Reporter2")

    resp = await client.post(
        REPORTS_URL,
        json={
            "target_type": "user",
            "target_id": str(uuid4()),
            "reason": "Test reason",
        },
        headers=auth_headers(reporter["session_token"]),
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# POST /reports -- self-report
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_create_report_self_report(client: AsyncClient) -> None:
    """User cannot report themselves: 400."""
    reporter = await login_user(client, telegram_id=59003, first_name="SelfReporter")

    resp = await client.post(
        REPORTS_URL,
        json={
            "target_type": "user",
            "target_id": reporter["user"]["id"],
            "reason": "I hate myself",
        },
        headers=auth_headers(reporter["session_token"]),
    )
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# POST /reports -- duplicate returns existing
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_create_report_duplicate(client: AsyncClient) -> None:
    """Duplicate report returns 200 with existing report + edit message."""
    reporter = await login_user(client, telegram_id=59004, first_name="DupReporter")
    target = await _create_target_user(client, telegram_id=59101)

    # First report -- 201.
    resp1 = await client.post(
        REPORTS_URL,
        json={
            "target_type": "user",
            "target_id": target["user"]["id"],
            "reason": "First reason",
        },
        headers=auth_headers(reporter["session_token"]),
    )
    assert resp1.status_code == 201

    # Second report on same target -- 200 with existing.
    resp2 = await client.post(
        REPORTS_URL,
        json={
            "target_type": "user",
            "target_id": target["user"]["id"],
            "reason": "Updated reason",
        },
        headers=auth_headers(reporter["session_token"]),
    )
    assert resp2.status_code == 200
    data = resp2.json()
    assert "message" in data
    assert "report" in data
    assert data["report"]["reason"] == "First reason"  # Not updated


# ---------------------------------------------------------------------------
# POST /reports -- practice target not found (real validation since Phase 4.1)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_create_report_practice_not_found(client: AsyncClient) -> None:
    """Practice target with non-existent id: 404."""
    reporter = await login_user(client, telegram_id=59005, first_name="PracReporter")

    resp = await client.post(
        REPORTS_URL,
        json={
            "target_type": "practice",
            "target_id": str(uuid4()),
            "reason": "Bad practice",
        },
        headers=auth_headers(reporter["session_token"]),
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# POST /reports -- invalid target_type
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_create_report_invalid_target_type(client: AsyncClient) -> None:
    """Invalid target_type: 422 (Pydantic Literal validation)."""
    reporter = await login_user(client, telegram_id=59006, first_name="BadType")

    resp = await client.post(
        REPORTS_URL,
        json={
            "target_type": "spaceship",
            "target_id": str(uuid4()),
            "reason": "Aliens",
        },
        headers=auth_headers(reporter["session_token"]),
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# POST /reports -- empty reason
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_create_report_empty_reason(client: AsyncClient) -> None:
    """Empty reason: 422."""
    reporter = await login_user(client, telegram_id=59007, first_name="EmptyReason")

    resp = await client.post(
        REPORTS_URL,
        json={
            "target_type": "user",
            "target_id": str(uuid4()),
            "reason": "",
        },
        headers=auth_headers(reporter["session_token"]),
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# PATCH /reports/{id} -- success
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_update_report_success(client: AsyncClient) -> None:
    """User can edit their own pending report."""
    reporter = await login_user(client, telegram_id=59008, first_name="Editor")
    target = await _create_target_user(client, telegram_id=59102)

    # Create report.
    resp1 = await client.post(
        REPORTS_URL,
        json={
            "target_type": "user",
            "target_id": target["user"]["id"],
            "reason": "Original reason",
        },
        headers=auth_headers(reporter["session_token"]),
    )
    report_id = resp1.json()["id"]

    # Edit report.
    resp2 = await client.patch(
        f"{REPORTS_URL}/{report_id}",
        json={"reason": "Updated reason"},
        headers=auth_headers(reporter["session_token"]),
    )
    assert resp2.status_code == 200
    assert resp2.json()["reason"] == "Updated reason"


# ---------------------------------------------------------------------------
# PATCH /reports/{id} -- not owner
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_update_report_not_owner(client: AsyncClient) -> None:
    """Cannot edit someone else's report: 404 (P-08)."""
    reporter = await login_user(client, telegram_id=59009, first_name="Owner")
    other = await login_user(client, telegram_id=59010, first_name="Other")
    target = await _create_target_user(client, telegram_id=59103)

    # Create report as reporter.
    resp1 = await client.post(
        REPORTS_URL,
        json={
            "target_type": "user",
            "target_id": target["user"]["id"],
            "reason": "My report",
        },
        headers=auth_headers(reporter["session_token"]),
    )
    report_id = resp1.json()["id"]

    # Try to edit as other user.
    resp2 = await client.patch(
        f"{REPORTS_URL}/{report_id}",
        json={"reason": "Hijacked"},
        headers=auth_headers(other["session_token"]),
    )
    # M-04 fix: 404 instead of 403 to avoid leaking resource existence (P-08).
    assert resp2.status_code == 404


# ---------------------------------------------------------------------------
# GET /reports/me -- list own reports
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_list_my_reports(client: AsyncClient) -> None:
    """User can list their own reports."""
    reporter = await login_user(client, telegram_id=59011, first_name="Lister")
    target = await _create_target_user(client, telegram_id=59104)

    # Create a report.
    await client.post(
        REPORTS_URL,
        json={
            "target_type": "user",
            "target_id": target["user"]["id"],
            "reason": "Some reason",
        },
        headers=auth_headers(reporter["session_token"]),
    )

    resp = await client.get(
        REPORTS_ME_URL,
        headers=auth_headers(reporter["session_token"]),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["reporter_id"] == reporter["user"]["id"]
