# =============================================================================
# Test: Users -- Master notification preferences (E8 contract)
# =============================================================================
#
# Covers the persisted master notifications contract: 9 toggles + a delivery
# schedule stored schema-on-read under credentials["master_notifications"] and
# exposed on UserResponse ONLY for role=master. Mirrors the existing 4-key
# user "notifications" suite, one band up.
#
# No delivery is asserted (push / quiet-hours are a separate track) -- only
# persistence, defaults, partial deep-merge, validation (422), role gating,
# and coexistence with the other credentials keys.
#
# telegram_id ranges:
#   89001          -- master (apply -> verified)
#   89900          -- admin (used to verify the master)
#   89002          -- plain user (non-master)
#   89003          -- user promoted to admin (admin sees None)
# =============================================================================

from collections.abc import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import User, UserRole
from tests.helpers import auth_headers, full_cleanup_range, login_user

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
ME_URL = "/api/v1/users/me"
APPLY_URL = "/api/v1/masters/apply"
VERIFY_URL = "/api/v1/admin/masters/{user_id}/verify"

_MASTER_TID = 89001
_ADMIN_TID = 89900

# Defaults asserted across several tests (all toggles True except monthly).
_DEFAULT_TOGGLES = {
    "new_booking": True,
    "booking_cancelled": True,
    "reminder": True,
    "new_checkin": True,
    "new_feedback": True,
    "msg_participants": True,
    "msg_support": True,
    "ai_summary": True,
    "monthly_report": False,
}
_DEFAULT_SCHEDULE = {
    "from": "08:00",
    "to": "22:00",
    "days": ["mon", "tue", "wed", "thu", "fri"],
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
async def cleanup(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    """Full ORM cleanup for telegram_id 89000-89999 before/after each test."""
    await _do_cleanup(db_session)
    yield
    await _do_cleanup(db_session)


async def _do_cleanup(session: AsyncSession) -> None:
    """Hard-delete the 89xxx test users before/after each test.

    delete_users=True (not just role reset) on purpose: these tests assert
    DEFAULT toggle/schedule values on a FRESH master, but full_cleanup_range
    does NOT clear the credentials JSONB on a role reset. A reused telegram_id
    would therefore carry master_notifications written by a previous test (even
    across runs) and break the "untouched == default" assertions. Deleting the
    users gives every test a clean credentials slate. Same pattern as
    test_admin_withdrawals; full_cleanup_range removes verification audit logs
    in FK-safe order, so deleting users in this range is safe.
    """
    await full_cleanup_range(session, 89000, 89999, delete_users=True)
    await session.commit()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _valid_apply_body() -> dict:
    """Return a valid MasterApplyRequest body."""
    return {
        "profile": {
            "display_name": "Notify Master",
            "email": "notify-master@test.com",
        },
        "experience": {
            "methods": ["meditation"],
            "experience_years": 5,
            "bio": "Master notifications test master",
        },
        "documents": [],
    }


async def _make_verified_master(
    client: AsyncClient,
    db_session: AsyncSession,
    telegram_id: int = _MASTER_TID,
) -> dict:
    """Create user, apply as master, verify via admin. Returns master auth."""
    auth = await login_user(
        client, telegram_id=telegram_id, first_name="Master",
    )
    await client.post(
        APPLY_URL,
        json=_valid_apply_body(),
        headers=auth_headers(auth["session_token"]),
    )

    # Promote admin and re-login to pick up the role.
    await login_user(client, telegram_id=_ADMIN_TID, first_name="Admin")
    await db_session.execute(
        update(User)
        .where(User.telegram_id == _ADMIN_TID)
        .values(role=UserRole.ADMIN.value)
    )
    await db_session.commit()
    admin_auth = await login_user(
        client, telegram_id=_ADMIN_TID, first_name="Admin",
    )

    user_id = auth["user"]["id"]
    verify_resp = await client.post(
        VERIFY_URL.format(user_id=user_id),
        json={},
        headers=auth_headers(admin_auth["session_token"]),
    )
    assert verify_resp.status_code == 200

    # Re-login to pick up the master role in the session.
    return await login_user(
        client, telegram_id=telegram_id, first_name="Master",
    )


async def _get_me(client: AsyncClient, token: str) -> dict:
    """GET /users/me -> JSON body (asserts 200)."""
    resp = await client.get(ME_URL, headers=auth_headers(token))
    assert resp.status_code == 200
    return resp.json()


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_master_notifications_defaults(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Fresh master: all toggles True except monthly_report; schedule default."""
    master = await _make_verified_master(client, db_session)
    body = await _get_me(client, master["session_token"])

    mn = body["master_notifications"]
    assert mn is not None
    for key, expected in _DEFAULT_TOGGLES.items():
        assert mn[key] is expected
    assert mn["schedule"] == _DEFAULT_SCHEDULE


# ---------------------------------------------------------------------------
# Partial toggle update keeps the others
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_master_notifications_partial_toggle_keeps_others(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Flipping one toggle leaves every other toggle and the schedule intact."""
    master = await _make_verified_master(client, db_session)
    token = master["session_token"]

    resp = await client.patch(
        ME_URL,
        json={"master_notifications": {"monthly_report": True}},
        headers=auth_headers(token),
    )
    assert resp.status_code == 200

    mn = resp.json()["master_notifications"]
    assert mn["monthly_report"] is True
    # Everything else untouched.
    assert mn["new_booking"] is True
    assert mn["ai_summary"] is True
    assert mn["msg_support"] is True
    assert mn["schedule"] == _DEFAULT_SCHEDULE


# ---------------------------------------------------------------------------
# Sequential updates accumulate
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_master_notifications_sequential_updates_accumulate(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Two separate PATCHes both stick (merge, not replace)."""
    master = await _make_verified_master(client, db_session)
    token = master["session_token"]

    await client.patch(
        ME_URL,
        json={"master_notifications": {"new_booking": False}},
        headers=auth_headers(token),
    )
    resp = await client.patch(
        ME_URL,
        json={"master_notifications": {"ai_summary": False}},
        headers=auth_headers(token),
    )
    assert resp.status_code == 200

    mn = resp.json()["master_notifications"]
    assert mn["new_booking"] is False
    assert mn["ai_summary"] is False
    # Untouched toggles stay at their defaults.
    assert mn["booking_cancelled"] is True
    assert mn["monthly_report"] is False


# ---------------------------------------------------------------------------
# Persist + survive relogin
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_master_notifications_persist_and_survive_relogin(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Stored prefs are still there after the master logs in again."""
    master = await _make_verified_master(client, db_session)
    token = master["session_token"]

    await client.patch(
        ME_URL,
        json={"master_notifications": {"msg_support": False, "reminder": False}},
        headers=auth_headers(token),
    )

    # Re-login (same telegram_id, still a master).
    relog = await login_user(
        client, telegram_id=_MASTER_TID, first_name="Master",
    )
    body = await _get_me(client, relog["session_token"])

    mn = body["master_notifications"]
    assert mn is not None
    assert mn["msg_support"] is False
    assert mn["reminder"] is False
    assert mn["new_booking"] is True


# ---------------------------------------------------------------------------
# Coexists with onboarding / phone / 4-key notifications (no cross-wipe)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_master_notifications_coexist_with_other_credentials(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """master_notifications and the other credentials keys do not clobber each
    other; the 4-key and 9-key notification objects stay distinct."""
    master = await _make_verified_master(client, db_session)
    token = master["session_token"]

    # Set onboarding + phone + the 4-key user notifications.
    resp1 = await client.patch(
        ME_URL,
        json={
            "onboarding_completed": True,
            "phone": "+7 916 000 11 22",
            "notifications": {"push": False},
        },
        headers=auth_headers(token),
    )
    assert resp1.status_code == 200

    # Set the master notifications (a toggle + a schedule sub-field).
    resp2 = await client.patch(
        ME_URL,
        json={
            "master_notifications": {
                "new_feedback": False,
                "schedule": {"to": "20:00"},
            },
        },
        headers=auth_headers(token),
    )
    assert resp2.status_code == 200

    body = await _get_me(client, token)

    # The other credentials keys survived.
    assert body["onboarding_completed"] is True
    assert body["phone"] == "+7 916 000 11 22"

    # 4-key notifications intact (push flipped, the rest default).
    assert body["notifications"]["push"] is False
    assert body["notifications"]["practice_reminders"] is True

    # master_notifications applied (toggle + schedule sub-field merged).
    mn = body["master_notifications"]
    assert mn["new_feedback"] is False
    assert mn["schedule"]["to"] == "20:00"
    assert mn["schedule"]["from"] == "08:00"

    # 4-key and 9-key are different shapes -- no key bleed between them.
    assert "new_feedback" not in body["notifications"]
    assert "push" not in mn


# ---------------------------------------------------------------------------
# Schedule partial update (and accumulation across sub-fields)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_master_notifications_schedule_partial_update(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Changing only `to` keeps from/days; a later days-only change accumulates."""
    master = await _make_verified_master(client, db_session)
    token = master["session_token"]

    resp = await client.patch(
        ME_URL,
        json={"master_notifications": {"schedule": {"to": "21:30"}}},
        headers=auth_headers(token),
    )
    assert resp.status_code == 200
    sched = resp.json()["master_notifications"]["schedule"]
    assert sched["to"] == "21:30"
    assert sched["from"] == "08:00"
    assert sched["days"] == ["mon", "tue", "wed", "thu", "fri"]

    # Change only days now -- the earlier `to` must persist.
    resp2 = await client.patch(
        ME_URL,
        json={"master_notifications": {"schedule": {"days": ["sat", "sun"]}}},
        headers=auth_headers(token),
    )
    assert resp2.status_code == 200
    sched2 = resp2.json()["master_notifications"]["schedule"]
    assert sched2["days"] == ["sat", "sun"]
    assert sched2["to"] == "21:30"
    assert sched2["from"] == "08:00"


# ---------------------------------------------------------------------------
# Empty days list is allowed
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_master_notifications_empty_days_allowed(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """An empty days list is a valid value (no weekday selected)."""
    master = await _make_verified_master(client, db_session)
    token = master["session_token"]

    resp = await client.patch(
        ME_URL,
        json={"master_notifications": {"schedule": {"days": []}}},
        headers=auth_headers(token),
    )
    assert resp.status_code == 200
    assert resp.json()["master_notifications"]["schedule"]["days"] == []


# ---------------------------------------------------------------------------
# Validation -- 422
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_master_notifications_bad_from_is_422(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """A malformed `from` time is rejected (24h HH:MM only)."""
    master = await _make_verified_master(client, db_session)
    token = master["session_token"]

    resp = await client.patch(
        ME_URL,
        json={"master_notifications": {"schedule": {"from": "25:00"}}},
        headers=auth_headers(token),
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_master_notifications_bad_to_is_422(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """A `to` time without a leading zero is rejected."""
    master = await _make_verified_master(client, db_session)
    token = master["session_token"]

    resp = await client.patch(
        ME_URL,
        json={"master_notifications": {"schedule": {"to": "8:00"}}},
        headers=auth_headers(token),
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_master_notifications_bad_day_code_is_422(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """An unknown weekday code is rejected (codes are mon..sun, not full names)."""
    master = await _make_verified_master(client, db_session)
    token = master["session_token"]

    resp = await client.patch(
        ME_URL,
        json={"master_notifications": {"schedule": {"days": ["mon", "monday"]}}},
        headers=auth_headers(token),
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Role gating -- exposed only to master
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_master_notifications_none_for_regular_user(
    client: AsyncClient,
) -> None:
    """A plain (non-master) user sees master_notifications == None."""
    auth = await login_user(client, telegram_id=89002, first_name="Regular")
    body = await _get_me(client, auth["session_token"])

    assert body["master_notifications"] is None
    # Sanity: the user still has the 4-key notifications object.
    assert body["notifications"] == {
        "push": True,
        "practice_reminders": True,
        "master_messages": True,
        "support_messages": True,
    }


@pytest.mark.asyncio
async def test_master_notifications_none_for_admin(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """An admin (role != master) also sees master_notifications == None."""
    auth = await login_user(client, telegram_id=89003, first_name="AdminUser")
    await db_session.execute(
        update(User)
        .where(User.telegram_id == 89003)
        .values(role=UserRole.ADMIN.value)
    )
    await db_session.commit()

    # Re-login to pick up the admin role in the session.
    auth = await login_user(client, telegram_id=89003, first_name="AdminUser")
    body = await _get_me(client, auth["session_token"])

    assert body["master_notifications"] is None
