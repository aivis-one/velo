# =============================================================================
# Test: Attendance -- Join, Leave, Finalize, List (Phase 5.4)
# =============================================================================
#
# telegram_id ranges:
#   63001-63099 -- master users
#   63100-63199 -- regular users (attendees)
#   63900-63999 -- admin users
# =============================================================================

from collections.abc import AsyncGenerator
from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers import auth_headers, login_user

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
BOOKINGS_URL = "/api/v1/bookings"
PRACTICES_URL = "/api/v1/practices"
APPLY_URL = "/api/v1/masters/apply"
VERIFY_URL = "/api/v1/admin/masters/{user_id}/verify"

# ---------------------------------------------------------------------------
# Cleanup (dependency order, modeled after test_cancellation.py)
# ---------------------------------------------------------------------------
_TID_RANGE = (
    "SELECT id FROM users WHERE telegram_id BETWEEN 63000 AND 63999"
)
_MASTER_RANGE = (
    "SELECT user_id FROM master_profiles "
    "WHERE user_id IN (" + _TID_RANGE + ")"
)

_CLEANUP_QUERIES = [
    # 1. Audit logs (table name: audit_logs, with 's').
    text(
        "DELETE FROM audit_logs WHERE actor_id IN (" + _TID_RANGE + ")"
    ),
    # 2. Company ledger (via purchases linked to our users).
    text(
        "DELETE FROM company_ledger WHERE reference_id IN "
        "(SELECT id FROM purchases WHERE user_id IN "
        "(" + _TID_RANGE + "))"
    ),
    # 3. Master ledger.
    text(
        "DELETE FROM master_ledger WHERE user_id IN (" + _TID_RANGE + ")"
    ),
    # 4. User ledger.
    text(
        "DELETE FROM user_ledger WHERE user_id IN (" + _TID_RANGE + ")"
    ),
    # 5. Nullify booking.purchase_id FK before deleting purchases.
    text(
        "UPDATE bookings SET purchase_id = NULL "
        "WHERE user_id IN (" + _TID_RANGE + ")"
    ),
    # 6. Purchases.
    text(
        "DELETE FROM purchases WHERE user_id IN (" + _TID_RANGE + ")"
    ),
    # 7. Waitlist (POST /cancel clears waitlist entries).
    text(
        "DELETE FROM waitlist WHERE user_id IN (" + _TID_RANGE + ")"
    ),
    # 8. Bookings.
    text(
        "DELETE FROM bookings WHERE user_id IN (" + _TID_RANGE + ")"
    ),
    # 9. Practices (owned by masters in our range).
    text(
        "DELETE FROM practices WHERE master_id IN "
        "(" + _MASTER_RANGE + ")"
    ),
    # 10. Master profiles.
    text(
        "DELETE FROM master_profiles WHERE user_id IN "
        "(" + _TID_RANGE + ")"
    ),
    # 11. Reset roles and balance.
    text(
        "UPDATE users SET role = 'user', balance_cents = 0 "
        "WHERE telegram_id BETWEEN 63000 AND 63999"
    ),
]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
async def _full_cleanup(db_session: AsyncSession) -> None:
    """Run all cleanup queries in dependency order."""
    for stmt in _CLEANUP_QUERIES:
        await db_session.execute(stmt)
    await db_session.commit()


@pytest.fixture(autouse=True)
async def cleanup(
    db_session: AsyncSession,
) -> AsyncGenerator[None, None]:
    """Clean all attendance-test data before and after each test."""
    await _full_cleanup(db_session)
    yield
    await _full_cleanup(db_session)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _valid_practice_body(**overrides: object) -> dict:
    """Return a valid CreatePracticeRequest body."""
    base = {
        "practice_type": "live",
        "title": "Attendance Test Session",
        "description": "Session for attendance testing",
        "scheduled_at": (
            datetime.now(timezone.utc) + timedelta(days=7)
        ).isoformat(),
        "duration_minutes": 60,
        "timezone": "Europe/Moscow",
        "max_participants": 10,
        "is_free": True,
        "price_cents": 0,
        "currency": "EUR",
    }
    base.update(overrides)
    return base


def _valid_apply_body() -> dict:
    return {
        "profile": {
            "display_name": "Attendance Master",
            "email": "attend-master@test.com",
        },
        "experience": {
            "methods": ["meditation"],
            "experience_years": 5,
            "bio": "Attendance test master",
        },
        "documents": [],
    }


async def _make_verified_master(
    client: AsyncClient,
    db_session: AsyncSession,
    telegram_id: int = 63001,
) -> dict:
    """Create user, apply, verify. Returns auth data."""
    auth = await login_user(
        client, telegram_id=telegram_id,
        first_name="Master",
    )
    await client.post(
        APPLY_URL,
        json=_valid_apply_body(),
        headers=auth_headers(auth["session_token"]),
    )

    admin_auth = await login_user(
        client, telegram_id=63900, first_name="Admin",
    )
    await db_session.execute(
        text(
            "UPDATE users SET role = 'admin' "
            "WHERE telegram_id = 63900"
        )
    )
    await db_session.commit()
    admin_auth = await login_user(
        client, telegram_id=63900, first_name="Admin",
    )

    user_id = auth["user"]["id"]
    verify_resp = await client.post(
        VERIFY_URL.format(user_id=user_id),
        json={},
        headers=auth_headers(admin_auth["session_token"]),
    )
    assert verify_resp.status_code == 200

    auth = await login_user(
        client, telegram_id=telegram_id,
        first_name="Master",
    )
    return auth


async def _create_scheduled_practice(
    client: AsyncClient,
    master_auth: dict,
    **overrides: object,
) -> str:
    """Create a practice and set status to scheduled."""
    body = _valid_practice_body(**overrides)
    resp = await client.post(
        PRACTICES_URL,
        json=body,
        headers=auth_headers(
            master_auth["session_token"],
        ),
    )
    assert resp.status_code == 201
    pid = resp.json()["id"]

    patch = await client.patch(
        f"{PRACTICES_URL}/{pid}",
        json={"status": "scheduled"},
        headers=auth_headers(
            master_auth["session_token"],
        ),
    )
    assert patch.status_code == 200
    return pid


async def _book_user(
    client: AsyncClient,
    practice_id: str,
    telegram_id: int,
) -> dict:
    """Book a user into a practice.
    Returns auth + booking_id."""
    user = await login_user(
        client, telegram_id=telegram_id, first_name="User",
    )
    resp = await client.post(
        BOOKINGS_URL,
        json={"practice_id": practice_id},
        headers=auth_headers(user["session_token"]),
    )
    assert resp.status_code == 201
    return {**user, "booking_id": resp.json()["id"]}


# ===================================================================
# POST /bookings/{id}/join -- check-in
# ===================================================================


@pytest.mark.asyncio
async def test_join_booking_success(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """User joins a scheduled practice: 200, joined_at set."""
    master = await _make_verified_master(client, db_session)
    pid = await _create_scheduled_practice(client, master)
    user_data = await _book_user(client, pid, telegram_id=63100)

    resp = await client.post(
        f"{BOOKINGS_URL}/{user_data['booking_id']}/join",
        headers=auth_headers(user_data["session_token"]),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["joined_at"] is not None
    assert data["status"] == "confirmed"


@pytest.mark.asyncio
async def test_join_booking_already_joined(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Double join: 409."""
    master = await _make_verified_master(client, db_session)
    pid = await _create_scheduled_practice(client, master)
    user_data = await _book_user(client, pid, telegram_id=63101)
    headers = auth_headers(user_data["session_token"])

    resp1 = await client.post(
        f"{BOOKINGS_URL}/{user_data['booking_id']}/join",
        headers=headers,
    )
    assert resp1.status_code == 200

    resp2 = await client.post(
        f"{BOOKINGS_URL}/{user_data['booking_id']}/join",
        headers=headers,
    )
    assert resp2.status_code == 409


@pytest.mark.asyncio
async def test_join_booking_not_owner(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Non-owner cannot join: 404 (P-08)."""
    master = await _make_verified_master(client, db_session)
    pid = await _create_scheduled_practice(client, master)
    user_data = await _book_user(client, pid, telegram_id=63102)

    other = await login_user(
        client, telegram_id=63103, first_name="Other",
    )
    resp = await client.post(
        f"{BOOKINGS_URL}/{user_data['booking_id']}/join",
        headers=auth_headers(other["session_token"]),
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_join_booking_cancelled_practice(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Cannot join cancelled practice: 400."""
    master = await _make_verified_master(client, db_session)
    pid = await _create_scheduled_practice(client, master)
    user_data = await _book_user(client, pid, telegram_id=63104)

    # Cancel the practice via POST /cancel (Phase 6.5).
    # PATCH status=cancelled is blocked in _VALID_TRANSITIONS.
    # POST /cancel also refunds all active bookings.
    cancel_resp = await client.post(
        f"{PRACTICES_URL}/{pid}/cancel",
        headers=auth_headers(master["session_token"]),
    )
    assert cancel_resp.status_code == 200

    # Booking is now cancelled -> join returns 400.
    resp = await client.post(
        f"{BOOKINGS_URL}/{user_data['booking_id']}/join",
        headers=auth_headers(user_data["session_token"]),
    )
    assert resp.status_code == 400


# ===================================================================
# POST /bookings/{id}/leave -- check-out
# ===================================================================


@pytest.mark.asyncio
async def test_leave_booking_success(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """User leaves after joining: 200, left_at set."""
    master = await _make_verified_master(client, db_session)
    pid = await _create_scheduled_practice(client, master)
    user_data = await _book_user(client, pid, telegram_id=63105)
    headers = auth_headers(user_data["session_token"])

    # Join first.
    await client.post(
        f"{BOOKINGS_URL}/{user_data['booking_id']}/join",
        headers=headers,
    )

    resp = await client.post(
        f"{BOOKINGS_URL}/{user_data['booking_id']}/leave",
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["left_at"] is not None


@pytest.mark.asyncio
async def test_leave_booking_without_join(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Cannot leave without joining first: 400."""
    master = await _make_verified_master(client, db_session)
    pid = await _create_scheduled_practice(client, master)
    user_data = await _book_user(client, pid, telegram_id=63106)

    resp = await client.post(
        f"{BOOKINGS_URL}/{user_data['booking_id']}/leave",
        headers=auth_headers(user_data["session_token"]),
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_leave_booking_already_left(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Double leave: 409."""
    master = await _make_verified_master(client, db_session)
    pid = await _create_scheduled_practice(client, master)
    user_data = await _book_user(client, pid, telegram_id=63107)
    headers = auth_headers(user_data["session_token"])

    await client.post(
        f"{BOOKINGS_URL}/{user_data['booking_id']}/join",
        headers=headers,
    )
    await client.post(
        f"{BOOKINGS_URL}/{user_data['booking_id']}/leave",
        headers=headers,
    )

    resp = await client.post(
        f"{BOOKINGS_URL}/{user_data['booking_id']}/leave",
        headers=headers,
    )
    assert resp.status_code == 409


# ===================================================================
# POST /practices/{id}/finalize -- master finalizes
# ===================================================================


@pytest.mark.asyncio
async def test_finalize_practice_success(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Finalize: joined -> attended, not joined -> no_show,
    practice -> completed."""
    master = await _make_verified_master(client, db_session)
    pid = await _create_scheduled_practice(client, master)

    # User A joins, User B does not.
    user_a = await _book_user(client, pid, telegram_id=63108)
    await _book_user(client, pid, telegram_id=63109)

    await client.post(
        f"{BOOKINGS_URL}/{user_a['booking_id']}/join",
        headers=auth_headers(user_a["session_token"]),
    )

    # Finalize.
    resp = await client.post(
        f"{PRACTICES_URL}/{pid}/finalize",
        headers=auth_headers(master["session_token"]),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"

    # Check attendance list.
    att_resp = await client.get(
        f"{PRACTICES_URL}/{pid}/attendance",
        headers=auth_headers(master["session_token"]),
    )
    assert att_resp.status_code == 200
    data = att_resp.json()
    assert data["attended"] == 1
    assert data["no_show"] == 1
    assert data["pending"] == 0


@pytest.mark.asyncio
async def test_finalize_practice_already_completed(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Cannot finalize twice: 400."""
    master = await _make_verified_master(client, db_session)
    pid = await _create_scheduled_practice(client, master)

    resp1 = await client.post(
        f"{PRACTICES_URL}/{pid}/finalize",
        headers=auth_headers(master["session_token"]),
    )
    assert resp1.status_code == 200

    resp2 = await client.post(
        f"{PRACTICES_URL}/{pid}/finalize",
        headers=auth_headers(master["session_token"]),
    )
    assert resp2.status_code == 400


@pytest.mark.asyncio
async def test_finalize_practice_not_owner(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Non-owner master cannot finalize: 404 (P-08)."""
    master = await _make_verified_master(client, db_session)
    pid = await _create_scheduled_practice(client, master)

    other_master = await _make_verified_master(
        client, db_session, telegram_id=63002,
    )
    resp = await client.post(
        f"{PRACTICES_URL}/{pid}/finalize",
        headers=auth_headers(other_master["session_token"]),
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_finalize_practice_non_master(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Regular user cannot finalize: 403."""
    master = await _make_verified_master(client, db_session)
    pid = await _create_scheduled_practice(client, master)

    user = await login_user(
        client, telegram_id=63110, first_name="User",
    )
    resp = await client.post(
        f"{PRACTICES_URL}/{pid}/finalize",
        headers=auth_headers(user["session_token"]),
    )
    assert resp.status_code == 403


# ===================================================================
# GET /practices/{id}/attendance -- attendance list
# ===================================================================


@pytest.mark.asyncio
async def test_attendance_list(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Attendance list shows all non-cancelled bookings."""
    master = await _make_verified_master(client, db_session)
    pid = await _create_scheduled_practice(client, master)

    user_a = await _book_user(client, pid, telegram_id=63111)
    await _book_user(client, pid, telegram_id=63112)

    # User A joins.
    await client.post(
        f"{BOOKINGS_URL}/{user_a['booking_id']}/join",
        headers=auth_headers(user_a["session_token"]),
    )

    resp = await client.get(
        f"{PRACTICES_URL}/{pid}/attendance",
        headers=auth_headers(master["session_token"]),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert data["pending"] == 2  # Not finalized yet.
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_attendance_list_not_owner(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Non-owner cannot view attendance: 404 (P-08)."""
    master = await _make_verified_master(client, db_session)
    pid = await _create_scheduled_practice(client, master)

    other_master = await _make_verified_master(
        client, db_session, telegram_id=63003,
    )
    resp = await client.get(
        f"{PRACTICES_URL}/{pid}/attendance",
        headers=auth_headers(other_master["session_token"]),
    )
    assert resp.status_code == 404
