# =============================================================================
# Test: Master methods change-request loop (M3 / E19-FLAT)
# =============================================================================
#
# Covers the FLAT method-change moderation loop:
#   POST /api/v1/masters/me/method-change-request            (master submit)
#   GET  /api/v1/admin/masters/method-change-requests        (admin list)
#   POST /api/v1/admin/masters/{id}/method-change-request/approve
#   POST /api/v1/admin/masters/{id}/method-change-request/reject
# plus the method_change_request projection on GET /api/v1/masters/me.
#
# telegram_id range (56600-56699 -- this module owns this sub-range):
#   56601        -- verified master (default)
#   56690        -- admin (ADMIN_TID)
# =============================================================================

from collections.abc import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import User, UserRole
from tests.helpers import auth_headers, full_cleanup_range, login_user, switch_self_to_master

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
APPLY_URL = "/api/v1/masters/apply"
VERIFY_URL = "/api/v1/admin/masters/{user_id}/verify"
ME_URL = "/api/v1/masters/me"
SUBMIT_URL = "/api/v1/masters/me/method-change-request"
LIST_URL = "/api/v1/admin/masters/method-change-requests"
APPROVE_URL = "/api/v1/admin/masters/{user_id}/method-change-request/approve"
REJECT_URL = "/api/v1/admin/masters/{user_id}/method-change-request/reject"

ADMIN_TID = 56690


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
async def cleanup(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    """Clean all test data before/after each test (ORM, no raw SQL)."""
    await _do_cleanup(db_session)
    yield
    await _do_cleanup(db_session)


async def _do_cleanup(session: AsyncSession) -> None:
    await full_cleanup_range(session, 56600, 56699, delete_users=False)
    await session.commit()


def _valid_apply_body() -> dict:
    return {
        "profile": {
            "display_name": "Method Master",
            "email": "mm@test.com",
            "phone": "+1234567890",
        },
        "experience": {
            "methods": ["Медитация", "Йога"],
            "experience_years": 5,
            "bio": "Practicing for years.",
            "certifications": [],
        },
        "documents": [],
    }


async def _make_admin_auth(
    client: AsyncClient,
    db_session: AsyncSession,
) -> dict:
    """Promote ADMIN_TID to admin and return a fresh admin auth."""
    await login_user(client, telegram_id=ADMIN_TID, first_name="Admin")
    await db_session.execute(
        update(User)
        .where(User.telegram_id == ADMIN_TID)
        .values(role=UserRole.ADMIN.value)
    )
    await db_session.commit()
    return await login_user(client, telegram_id=ADMIN_TID, first_name="Admin")


async def _make_verified_master(
    client: AsyncClient,
    db_session: AsyncSession,
    telegram_id: int = 56601,
) -> dict:
    """Create user, apply, verify via admin. Returns master auth (post-verify)."""
    auth = await login_user(client, telegram_id=telegram_id, first_name="Master")
    await client.post(
        APPLY_URL,
        json=_valid_apply_body(),
        headers=auth_headers(auth["session_token"]),
    )

    admin_auth = await _make_admin_auth(client, db_session)
    user_id = auth["user"]["id"]
    verify_resp = await client.post(
        VERIFY_URL.format(user_id=user_id),
        json={},
        headers=auth_headers(admin_auth["session_token"]),
    )
    assert verify_resp.status_code == 200

    # Re-login to pick up master role in the session.
    await switch_self_to_master(client, auth["session_token"])
    return await login_user(client, telegram_id=telegram_id, first_name="Master")


# ---------------------------------------------------------------------------
# GET /me exposure (no request)
# ---------------------------------------------------------------------------
async def test_me_has_null_method_change_request_by_default(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """A verified master with no request exposes method_change_request=None."""
    master = await _make_verified_master(client, db_session)
    resp = await client.get(
        ME_URL, headers=auth_headers(master["session_token"])
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "method_change_request" in body
    assert body["method_change_request"] is None


# ---------------------------------------------------------------------------
# Submit
# ---------------------------------------------------------------------------
async def test_master_submit_creates_pending_request(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Submit stores a pending request; live methods stay unchanged."""
    master = await _make_verified_master(client, db_session)
    headers = auth_headers(master["session_token"])

    resp = await client.post(
        SUBMIT_URL,
        json={"proposed_methods": ["Йога", "Звукотерапия"]},
        headers=headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    mcr = body["method_change_request"]
    assert mcr is not None
    assert mcr["status"] == "pending"
    assert mcr["proposed_methods"] == ["Йога", "Звукотерапия"]
    # Live methods NOT touched until approval.
    assert body["methods"] == ["Медитация", "Йога"]


async def test_duplicate_pending_submit_conflicts(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """A second submit while one is pending returns 409 method_change_pending."""
    master = await _make_verified_master(client, db_session)
    headers = auth_headers(master["session_token"])

    first = await client.post(
        SUBMIT_URL, json={"proposed_methods": ["Йога"]}, headers=headers
    )
    assert first.status_code == 201

    second = await client.post(
        SUBMIT_URL, json={"proposed_methods": ["Медитация"]}, headers=headers
    )
    assert second.status_code == 409
    assert second.json()["error"] == "method_change_pending"


async def test_submit_validation_rejects_empty_methods(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """proposed_methods must have at least one entry (422)."""
    master = await _make_verified_master(client, db_session)
    resp = await client.post(
        SUBMIT_URL,
        json={"proposed_methods": []},
        headers=auth_headers(master["session_token"]),
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Admin list
# ---------------------------------------------------------------------------
async def test_admin_list_shows_pending_request(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """The admin list surfaces the pending request with current + proposed."""
    master = await _make_verified_master(client, db_session)
    master_id = master["user"]["id"]
    await client.post(
        SUBMIT_URL,
        json={"proposed_methods": ["Йога", "Звукотерапия"]},
        headers=auth_headers(master["session_token"]),
    )

    admin_auth = await _make_admin_auth(client, db_session)
    resp = await client.get(
        LIST_URL, headers=auth_headers(admin_auth["session_token"])
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    item = body["items"][0]
    assert item["user_id"] == master_id
    assert item["current_methods"] == ["Медитация", "Йога"]
    assert item["proposed_methods"] == ["Йога", "Звукотерапия"]


async def test_admin_list_requires_admin(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """A non-admin (the master) cannot read the moderation list (403)."""
    master = await _make_verified_master(client, db_session)
    resp = await client.get(
        LIST_URL, headers=auth_headers(master["session_token"])
    )
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Approve
# ---------------------------------------------------------------------------
async def test_admin_approve_updates_methods_and_clears_request(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Approve copies proposed into live methods and clears the request."""
    master = await _make_verified_master(client, db_session)
    master_id = master["user"]["id"]
    master_headers = auth_headers(master["session_token"])
    await client.post(
        SUBMIT_URL,
        json={"proposed_methods": ["Йога", "Звукотерапия"]},
        headers=master_headers,
    )

    admin_auth = await _make_admin_auth(client, db_session)
    approve = await client.post(
        APPROVE_URL.format(user_id=master_id),
        json={},
        headers=auth_headers(admin_auth["session_token"]),
    )
    assert approve.status_code == 200
    assert approve.json()["status"] == "approved"

    # Master profile now carries the new methods, no outstanding request.
    me = await client.get(ME_URL, headers=master_headers)
    body = me.json()
    assert body["methods"] == ["Йога", "Звукотерапия"]
    assert body["method_change_request"] is None

    # List is empty again.
    empty = await client.get(
        LIST_URL, headers=auth_headers(admin_auth["session_token"])
    )
    assert empty.json()["total"] == 0


async def test_approve_without_pending_is_404(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Approving when there is no pending request returns 404."""
    master = await _make_verified_master(client, db_session)
    master_id = master["user"]["id"]
    admin_auth = await _make_admin_auth(client, db_session)
    resp = await client.post(
        APPROVE_URL.format(user_id=master_id),
        json={},
        headers=auth_headers(admin_auth["session_token"]),
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Reject
# ---------------------------------------------------------------------------
async def test_admin_reject_keeps_methods_and_records_reason(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Reject leaves live methods and surfaces status+reason to the master."""
    master = await _make_verified_master(client, db_session)
    master_id = master["user"]["id"]
    master_headers = auth_headers(master["session_token"])
    await client.post(
        SUBMIT_URL,
        json={"proposed_methods": ["Звукотерапия"]},
        headers=master_headers,
    )

    admin_auth = await _make_admin_auth(client, db_session)
    reject = await client.post(
        REJECT_URL.format(user_id=master_id),
        json={"reason": "Недостаточно опыта в этом направлении"},
        headers=auth_headers(admin_auth["session_token"]),
    )
    assert reject.status_code == 200
    assert reject.json()["status"] == "rejected"

    me = await client.get(ME_URL, headers=master_headers)
    body = me.json()
    # Live methods unchanged.
    assert body["methods"] == ["Медитация", "Йога"]
    mcr = body["method_change_request"]
    assert mcr is not None
    assert mcr["status"] == "rejected"
    assert mcr["reject_reason"] == "Недостаточно опыта в этом направлении"

    # No longer pending -> not in the admin list.
    empty = await client.get(
        LIST_URL, headers=auth_headers(admin_auth["session_token"])
    )
    assert empty.json()["total"] == 0


async def test_reject_requires_reason(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Reject with an empty reason is rejected by validation (422)."""
    master = await _make_verified_master(client, db_session)
    master_id = master["user"]["id"]
    await client.post(
        SUBMIT_URL,
        json={"proposed_methods": ["Звукотерапия"]},
        headers=auth_headers(master["session_token"]),
    )
    admin_auth = await _make_admin_auth(client, db_session)
    resp = await client.post(
        REJECT_URL.format(user_id=master_id),
        json={"reason": ""},
        headers=auth_headers(admin_auth["session_token"]),
    )
    assert resp.status_code == 422


async def test_master_can_resubmit_after_rejection(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """A rejected request does not block a fresh submit."""
    master = await _make_verified_master(client, db_session)
    master_id = master["user"]["id"]
    master_headers = auth_headers(master["session_token"])
    await client.post(
        SUBMIT_URL,
        json={"proposed_methods": ["Звукотерапия"]},
        headers=master_headers,
    )
    admin_auth = await _make_admin_auth(client, db_session)
    await client.post(
        REJECT_URL.format(user_id=master_id),
        json={"reason": "no"},
        headers=auth_headers(admin_auth["session_token"]),
    )

    # A new submit is allowed and becomes pending again.
    resub = await client.post(
        SUBMIT_URL,
        json={"proposed_methods": ["Йога"]},
        headers=master_headers,
    )
    assert resub.status_code == 201
    assert resub.json()["method_change_request"]["status"] == "pending"
