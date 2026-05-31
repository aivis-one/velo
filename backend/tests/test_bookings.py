# =============================================================================
# Test: Bookings -- Create + Cancel (Phase 5.1+5.2, updated Phase 6.4)
# =============================================================================
#
# telegram_id ranges:
#   61001-61099 -- master users
#   61100-61199 -- regular users (bookers)
#   61900-61999 -- admin users
# =============================================================================

from collections.abc import AsyncGenerator
from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.practices.models import Practice
from app.modules.users.models import User, UserRole
from tests.helpers import auth_headers, login_user, full_cleanup_range

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
BOOKINGS_URL = "/api/v1/bookings"
PRACTICES_URL = "/api/v1/practices"
APPLY_URL = "/api/v1/masters/apply"
VERIFY_URL = "/api/v1/admin/masters/{user_id}/verify"

# Cleanup in dependency order (ledger -> purchases -> bookings -> practices).

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
    """Full ORM cleanup for telegram_id 61000-61999."""
    await full_cleanup_range(session, 61000, 61999, delete_users=False)
    await session.commit()



# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _valid_practice_body(**overrides: object) -> dict:
    """Return a valid CreatePracticeRequest body."""
    base = {
        "practice_type": "live",
        "direction": "meditation",
        "difficulty": "beginner",
        "title": "Morning Meditation",
        "description": "Guided breathwork session",
        "scheduled_at": (
            datetime.now(timezone.utc) + timedelta(days=7)
        ).isoformat(),
        "duration_minutes": 60,
        "timezone": "Europe/Moscow",
        "max_participants": 20,
        "is_free": True,
        "price_cents": 0,
        "currency": "eur",
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
    telegram_id: int = 61001,
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
        client, telegram_id=61900, first_name="Admin",
    )
    await db_session.execute(
    update(User)
    .where(User.telegram_id == 61900)
    .values(role=UserRole.ADMIN.value)
)
    await db_session.commit()
    admin_auth = await login_user(
        client, telegram_id=61900, first_name="Admin",
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


# ===================================================================
# POST /bookings -- create
# ===================================================================


@pytest.mark.asyncio
async def test_create_booking_success(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """User books a free scheduled practice: 201, confirmed."""
    master = await _make_verified_master(
        client, db_session,
    )
    pid = await _create_scheduled_practice(client, master)

    user = await login_user(
        client, telegram_id=61101, first_name="User",
    )
    resp = await client.post(
        BOOKINGS_URL,
        json={"practice_id": pid},
        headers=auth_headers(user["session_token"]),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "confirmed"
    assert data["practice_id"] == pid


@pytest.mark.asyncio
async def test_create_booking_no_auth(
    client: AsyncClient,
) -> None:
    """No auth: 401."""
    resp = await client.post(
        BOOKINGS_URL,
        json={"practice_id": "00000000-0000-0000-0000-000000000001"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_create_booking_practice_not_found(
    client: AsyncClient,
) -> None:
    """Non-existent practice: 404."""
    user = await login_user(
        client, telegram_id=61102, first_name="User",
    )
    resp = await client.post(
        BOOKINGS_URL,
        json={
            "practice_id":
                "00000000-0000-0000-0000-000000000001",
        },
        headers=auth_headers(user["session_token"]),
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_booking_draft_practice(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Cannot book a draft practice: 400."""
    master = await _make_verified_master(
        client, db_session,
    )
    # Create but do NOT schedule.
    resp = await client.post(
        PRACTICES_URL,
        json=_valid_practice_body(),
        headers=auth_headers(
            master["session_token"],
        ),
    )
    assert resp.status_code == 201
    pid = resp.json()["id"]

    user = await login_user(
        client, telegram_id=61103, first_name="User",
    )
    resp = await client.post(
        BOOKINGS_URL,
        json={"practice_id": pid},
        headers=auth_headers(user["session_token"]),
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_create_booking_past_practice(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Cannot book a practice that has already started: 400.

    The CreatePracticeRequest validator rejects a past scheduled_at, so the
    practice is created in the future (scheduled) and then moved into the
    past directly via ORM -- the only honest way to reach the "already
    started" state (a forgetful master / not-yet-run auto-finalizer leaves
    the practice `scheduled` past its start). The booking endpoint must
    refuse it even though the status is still scheduled.
    """
    master = await _make_verified_master(client, db_session)
    pid = await _create_scheduled_practice(client, master)

    # Move the practice one hour into the past (still status=scheduled).
    await db_session.execute(
        update(Practice)
        .where(Practice.id == pid)
        .values(
            scheduled_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
    )
    await db_session.commit()

    # Sanity: the update is committed and visible (a fresh read sees the
    # past scheduled_at). Guards against a silent no-op update masking the
    # real assertion below.
    db_session.expire_all()
    moved = await db_session.get(Practice, UUID(pid))
    assert moved is not None
    assert moved.scheduled_at < datetime.now(timezone.utc)

    user = await login_user(
        client, telegram_id=61114, first_name="User",
    )
    resp = await client.post(
        BOOKINGS_URL,
        json={"practice_id": pid},
        headers=auth_headers(user["session_token"]),
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_create_booking_own_practice(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Master cannot book own practice: 400."""
    master = await _make_verified_master(
        client, db_session,
    )
    pid = await _create_scheduled_practice(client, master)

    resp = await client.post(
        BOOKINGS_URL,
        json={"practice_id": pid},
        headers=auth_headers(
            master["session_token"],
        ),
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_create_booking_paid_practice_insufficient_balance(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Paid practice with zero balance: 400 Insufficient balance."""
    master = await _make_verified_master(
        client, db_session,
    )
    pid = await _create_scheduled_practice(
        client, master,
        is_free=False, price_cents=1500,
    )

    user = await login_user(
        client, telegram_id=61104, first_name="User",
    )
    resp = await client.post(
        BOOKINGS_URL,
        json={"practice_id": pid},
        headers=auth_headers(user["session_token"]),
    )
    assert resp.status_code == 400
    assert "Insufficient balance" in resp.json()["message"]


@pytest.mark.asyncio
async def test_create_booking_duplicate(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Duplicate booking: 409."""
    master = await _make_verified_master(
        client, db_session,
    )
    pid = await _create_scheduled_practice(client, master)

    user = await login_user(
        client, telegram_id=61105, first_name="User",
    )
    headers = auth_headers(user["session_token"])

    resp1 = await client.post(
        BOOKINGS_URL,
        json={"practice_id": pid},
        headers=headers,
    )
    assert resp1.status_code == 201

    resp2 = await client.post(
        BOOKINGS_URL,
        json={"practice_id": pid},
        headers=headers,
    )
    assert resp2.status_code == 409


@pytest.mark.asyncio
async def test_create_booking_full_capacity(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Practice at max capacity: 400."""
    master = await _make_verified_master(
        client, db_session,
    )
    pid = await _create_scheduled_practice(
        client, master, max_participants=1,
    )

    # First booking fills the slot.
    user1 = await login_user(
        client, telegram_id=61106, first_name="User1",
    )
    resp1 = await client.post(
        BOOKINGS_URL,
        json={"practice_id": pid},
        headers=auth_headers(user1["session_token"]),
    )
    assert resp1.status_code == 201

    # Second booking: full.
    user2 = await login_user(
        client, telegram_id=61107, first_name="User2",
    )
    resp2 = await client.post(
        BOOKINGS_URL,
        json={"practice_id": pid},
        headers=auth_headers(user2["session_token"]),
    )
    assert resp2.status_code == 400


# ===================================================================
# DELETE /bookings/{id} -- cancel
# ===================================================================


@pytest.mark.asyncio
async def test_cancel_booking_success(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """User cancels own booking: 200, cancelled."""
    master = await _make_verified_master(
        client, db_session,
    )
    pid = await _create_scheduled_practice(client, master)

    user = await login_user(
        client, telegram_id=61108, first_name="User",
    )
    create_resp = await client.post(
        BOOKINGS_URL,
        json={"practice_id": pid},
        headers=auth_headers(user["session_token"]),
    )
    assert create_resp.status_code == 201
    bid = create_resp.json()["id"]

    resp = await client.delete(
        f"{BOOKINGS_URL}/{bid}",
        headers=auth_headers(user["session_token"]),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "cancelled"
    assert data["cancelled_at"] is not None


@pytest.mark.asyncio
async def test_cancel_booking_with_reason(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Cancel with reason: reason saved."""
    master = await _make_verified_master(
        client, db_session,
    )
    pid = await _create_scheduled_practice(client, master)

    user = await login_user(
        client, telegram_id=61109, first_name="User",
    )
    create_resp = await client.post(
        BOOKINGS_URL,
        json={"practice_id": pid},
        headers=auth_headers(user["session_token"]),
    )
    assert create_resp.status_code == 201
    bid = create_resp.json()["id"]

    resp = await client.request(
        "DELETE",
        f"{BOOKINGS_URL}/{bid}",
        json={"reason": "Changed my mind"},
        headers=auth_headers(user["session_token"]),
    )
    assert resp.status_code == 200
    assert resp.json()["cancellation_reason"] == (
        "Changed my mind"
    )


@pytest.mark.asyncio
async def test_cancel_booking_not_owner(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Non-owner cannot cancel: 404 (P-08)."""
    master = await _make_verified_master(
        client, db_session,
    )
    pid = await _create_scheduled_practice(client, master)

    user1 = await login_user(
        client, telegram_id=61110, first_name="User1",
    )
    create_resp = await client.post(
        BOOKINGS_URL,
        json={"practice_id": pid},
        headers=auth_headers(user1["session_token"]),
    )
    assert create_resp.status_code == 201
    bid = create_resp.json()["id"]

    user2 = await login_user(
        client, telegram_id=61111, first_name="User2",
    )
    resp = await client.delete(
        f"{BOOKINGS_URL}/{bid}",
        headers=auth_headers(user2["session_token"]),
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_cancel_booking_not_found(
    client: AsyncClient,
) -> None:
    """Non-existent booking: 404."""
    user = await login_user(
        client, telegram_id=61112, first_name="User",
    )
    resp = await client.delete(
        f"{BOOKINGS_URL}/"
        "00000000-0000-0000-0000-000000000001",
        headers=auth_headers(user["session_token"]),
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_cancel_already_cancelled(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Cannot cancel an already cancelled booking: 400."""
    master = await _make_verified_master(
        client, db_session,
    )
    pid = await _create_scheduled_practice(client, master)

    user = await login_user(
        client, telegram_id=61113, first_name="User",
    )
    headers = auth_headers(user["session_token"])

    create_resp = await client.post(
        BOOKINGS_URL,
        json={"practice_id": pid},
        headers=headers,
    )
    assert create_resp.status_code == 201
    bid = create_resp.json()["id"]

    # Cancel once.
    resp1 = await client.delete(
        f"{BOOKINGS_URL}/{bid}", headers=headers,
    )
    assert resp1.status_code == 200

    # Cancel again.
    resp2 = await client.delete(
        f"{BOOKINGS_URL}/{bid}", headers=headers,
    )
    assert resp2.status_code == 400
