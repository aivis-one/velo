# =============================================================================
# Test: Admin Reports -- resolve, dismiss, listing (Phase 3.3)
# =============================================================================
#
# telegram_id ranges:
#   59200-59299 -- reporters
#   59300-59399 -- targets
#   59900-59999 -- admin users
# =============================================================================

from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import User, UserRole
from tests.helpers import auth_headers, login_user, full_cleanup_range

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
REPORTS_URL = "/api/v1/reports"
ADMIN_REPORTS_URL = "/api/v1/admin/reports"
RESOLVE_URL = "/api/v1/admin/reports/{report_id}/resolve"
DISMISS_URL = "/api/v1/admin/reports/{report_id}/dismiss"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
async def cleanup(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    """Clean all test data before/after each test (TD-032: ORM, no raw SQL)."""
    await _do_cleanup(db_session)
    yield
    await _do_cleanup(db_session)


async def _do_cleanup(session: AsyncSession) -> None:
    """Full ORM cleanup for telegram_id 59200-59999."""
    await full_cleanup_range(session, 59200, 59999, delete_users=False)
    await session.commit()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
async def _make_admin(
    client: AsyncClient,
    db_session: AsyncSession,
    telegram_id: int = 59900,
) -> str:
    """Create admin user, return token."""
    auth = await login_user(
        client, telegram_id=telegram_id, first_name="ReportAdmin"
    )
    await db_session.execute(
        update(User)
        .where(User.id == auth["user"]["id"])
        .values(role=UserRole.ADMIN.value)
    )
    await db_session.commit()
    return auth["session_token"]


async def _create_report(
    client: AsyncClient,
    reporter_tg_id: int,
    target_tg_id: int,
    reason: str = "Test reason",
) -> tuple[str, str, str]:
    """Create reporter + target + report.

    Returns (reporter_token, target_id, report_id).
    """
    reporter = await login_user(
        client, telegram_id=reporter_tg_id, first_name=f"Reporter{reporter_tg_id}"
    )
    target = await login_user(
        client, telegram_id=target_tg_id, first_name=f"Target{target_tg_id}"
    )

    resp = await client.post(
        REPORTS_URL,
        json={
            "target_type": "user",
            "target_id": target["user"]["id"],
            "reason": reason,
        },
        headers=auth_headers(reporter["session_token"]),
    )
    assert resp.status_code == 201

    return (
        reporter["session_token"],
        target["user"]["id"],
        resp.json()["id"],
    )


# ---------------------------------------------------------------------------
# GET /admin/reports -- auth checks
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_list_reports_no_auth(client: AsyncClient) -> None:
    """No token: 401."""
    resp = await client.get(ADMIN_REPORTS_URL)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_list_reports_non_admin(client: AsyncClient) -> None:
    """Regular user: 403."""
    auth = await login_user(client, telegram_id=59200, first_name="NotAdmin")
    resp = await client.get(
        ADMIN_REPORTS_URL, headers=auth_headers(auth["session_token"])
    )
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# GET /admin/reports -- listing
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_list_reports_success(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Admin can list reports with pagination."""
    token = await _make_admin(client, db_session)

    # Create a report.
    await _create_report(client, reporter_tg_id=59201, target_tg_id=59301)

    resp = await client.get(ADMIN_REPORTS_URL, headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_list_reports_filter_status(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Filter by status returns only matching reports."""
    token = await _make_admin(client, db_session)

    # Create and resolve a report.
    _, _, report_id = await _create_report(
        client, reporter_tg_id=59202, target_tg_id=59302
    )
    resolve_url = RESOLVE_URL.format(report_id=report_id)
    await client.post(
        resolve_url,
        json={"resolution_note": "Resolved"},
        headers=auth_headers(token),
    )

    # Filter by pending -- resolved report should not appear.
    resp = await client.get(
        f"{ADMIN_REPORTS_URL}?status=pending",
        headers=auth_headers(token),
    )
    data = resp.json()
    for item in data["items"]:
        assert item["status"] == "pending"


@pytest.mark.asyncio
async def test_list_reports_filter_target_type(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Filter by target_type works."""
    token = await _make_admin(client, db_session)

    await _create_report(client, reporter_tg_id=59203, target_tg_id=59303)

    resp = await client.get(
        f"{ADMIN_REPORTS_URL}?target_type=user",
        headers=auth_headers(token),
    )
    data = resp.json()
    for item in data["items"]:
        assert item["target_type"] == "user"


# ---------------------------------------------------------------------------
# POST /admin/reports/{id}/resolve -- success
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_resolve_report_success(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Admin can resolve a pending report."""
    token = await _make_admin(client, db_session, telegram_id=59901)
    _, _, report_id = await _create_report(
        client, reporter_tg_id=59204, target_tg_id=59304
    )

    url = RESOLVE_URL.format(report_id=report_id)
    resp = await client.post(
        url,
        json={"resolution_note": "User warned"},
        headers=auth_headers(token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "resolved"
    assert data["resolution_note"] == "User warned"
    assert data["resolved_by"] is not None
    assert data["resolved_at"] is not None


# ---------------------------------------------------------------------------
# POST /admin/reports/{id}/resolve -- no auth
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_resolve_report_no_auth(client: AsyncClient) -> None:
    """No token: 401."""
    url = RESOLVE_URL.format(report_id=uuid4())
    resp = await client.post(url, json={"resolution_note": "Test"})
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# POST /admin/reports/{id}/resolve -- not found
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_resolve_report_not_found(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Non-existent report: 404."""
    token = await _make_admin(client, db_session, telegram_id=59902)

    url = RESOLVE_URL.format(report_id=uuid4())
    resp = await client.post(
        url,
        json={"resolution_note": "Test"},
        headers=auth_headers(token),
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# POST /admin/reports/{id}/resolve -- already resolved
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_resolve_already_resolved(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Resolving an already-resolved report: 409."""
    token = await _make_admin(client, db_session, telegram_id=59903)
    _, _, report_id = await _create_report(
        client, reporter_tg_id=59205, target_tg_id=59305
    )

    url = RESOLVE_URL.format(report_id=report_id)

    # First resolve -- success.
    resp1 = await client.post(
        url,
        json={"resolution_note": "Done"},
        headers=auth_headers(token),
    )
    assert resp1.status_code == 200

    # Second resolve -- conflict.
    resp2 = await client.post(
        url,
        json={"resolution_note": "Again"},
        headers=auth_headers(token),
    )
    assert resp2.status_code == 409


# ---------------------------------------------------------------------------
# POST /admin/reports/{id}/resolve -- empty note
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_resolve_empty_note(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Resolve without note: 422."""
    token = await _make_admin(client, db_session, telegram_id=59904)

    url = RESOLVE_URL.format(report_id=uuid4())
    resp = await client.post(
        url,
        json={"resolution_note": ""},
        headers=auth_headers(token),
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# POST /admin/reports/{id}/dismiss -- success
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_dismiss_report_success(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Admin can dismiss a pending report."""
    token = await _make_admin(client, db_session, telegram_id=59905)
    _, _, report_id = await _create_report(
        client, reporter_tg_id=59206, target_tg_id=59306
    )

    url = DISMISS_URL.format(report_id=report_id)
    resp = await client.post(
        url,
        json={"resolution_note": "Not a real issue"},
        headers=auth_headers(token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "dismissed"


# ---------------------------------------------------------------------------
# POST /admin/reports/{id}/dismiss -- without note (optional)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_dismiss_without_note(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Dismiss without resolution_note (optional): 200."""
    token = await _make_admin(client, db_session, telegram_id=59906)
    _, _, report_id = await _create_report(
        client, reporter_tg_id=59207, target_tg_id=59307
    )

    url = DISMISS_URL.format(report_id=report_id)
    resp = await client.post(
        url,
        json={},
        headers=auth_headers(token),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "dismissed"


# ---------------------------------------------------------------------------
# POST /admin/reports/{id}/dismiss -- already dismissed
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_dismiss_already_dismissed(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Dismissing an already-dismissed report: 409."""
    token = await _make_admin(client, db_session, telegram_id=59907)
    _, _, report_id = await _create_report(
        client, reporter_tg_id=59208, target_tg_id=59308
    )

    url = DISMISS_URL.format(report_id=report_id)

    # First dismiss -- success.
    resp1 = await client.post(url, json={}, headers=auth_headers(token))
    assert resp1.status_code == 200

    # Second dismiss -- conflict.
    resp2 = await client.post(url, json={}, headers=auth_headers(token))
    assert resp2.status_code == 409


# ---------------------------------------------------------------------------
# Lifecycle: resolve dismissed report (cross-state)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_resolve_dismissed_report(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Cannot resolve a dismissed report: 409."""
    token = await _make_admin(client, db_session, telegram_id=59908)
    _, _, report_id = await _create_report(
        client, reporter_tg_id=59209, target_tg_id=59309
    )

    # Dismiss first.
    dismiss_url = DISMISS_URL.format(report_id=report_id)
    resp1 = await client.post(dismiss_url, json={}, headers=auth_headers(token))
    assert resp1.status_code == 200

    # Try to resolve.
    resolve_url = RESOLVE_URL.format(report_id=report_id)
    resp2 = await client.post(
        resolve_url,
        json={"resolution_note": "Oops"},
        headers=auth_headers(token),
    )
    assert resp2.status_code == 409
