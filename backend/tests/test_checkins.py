# =============================================================================
# VELO Backend -- Tests: Diary Check-ins (Phase 8.1)
# =============================================================================
#
# telegram_id range: 85000-85999
#
# Coverage:
#   - POST /practices/{id}/checkin (upsert)
#   - GET /users/me/checkins (paginated, filtered)
#   - Window validation (too early, too late)
#   - Booking status validation (only confirmed)
#   - Upsert semantics (create, then update)
#   - Comment length validation
#   - Auth checks (401, no booking 404)
# =============================================================================

from datetime import UTC, datetime, timedelta
from unittest.mock import patch
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.bookings.models import Booking, BookingStatus
from app.modules.diary.models import CheckType, Checkin, Mood
from app.modules.masters.models import MasterProfile
from app.modules.practices.models import Practice, PracticeStatus, PracticeType
from app.modules.users.models import User, UserRole
from tests.helpers import auth_headers, login_user

CHECKIN_URL = "/api/v1/practices/{practice_id}/checkin"
MY_CHECKINS_URL = "/api/v1/users/me/checkins"


# ===================================================================
# Helpers
# ===================================================================


async def _make_verified_master(
    client: AsyncClient,
    db_session: AsyncSession,
    telegram_id: int = 85900,
) -> dict:
    """Create a verified master and return auth dict."""
    auth = await login_user(client, telegram_id=telegram_id, first_name="Master")
    user_id = auth["user"]["id"]

    user = await db_session.get(User, user_id)
    user.role = UserRole.MASTER
    await db_session.flush()

    profile = MasterProfile(
        user_id=user_id,
        data={
            "account": {"status": "verified"},
            "profile": {"bio": "Test master"},
        },
    )
    db_session.add(profile)
    await db_session.flush()

    return auth


async def _create_practice(
    db_session: AsyncSession,
    master_id: str,
    *,
    scheduled_at: datetime | None = None,
    status: str = PracticeStatus.SCHEDULED.value,
) -> Practice:
    """Create a practice for testing."""
    if scheduled_at is None:
        # Default: 2 hours from now (within check-in window).
        scheduled_at = datetime.now(UTC) + timedelta(hours=2)

    practice = Practice(
        master_id=master_id,
        title="Test Practice",
        description="Test description",
        practice_type=PracticeType.LIVE.value,
        status=status,
        scheduled_at=scheduled_at,
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


async def _create_confirmed_booking(
    db_session: AsyncSession,
    user_id: str,
    practice_id,
) -> Booking:
    """Create a confirmed booking for testing."""
    booking = Booking(
        practice_id=practice_id,
        user_id=user_id,
        status=BookingStatus.CONFIRMED.value,
    )
    db_session.add(booking)
    await db_session.flush()
    return booking


# ===================================================================
# POST /practices/{id}/checkin -- happy path (create)
# ===================================================================


@pytest.mark.asyncio
async def test_checkin_create_success(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Create a new check-in: 200, mood saved."""
    master_auth = await _make_verified_master(
        client, db_session, telegram_id=85901,
    )
    auth = await login_user(client, telegram_id=85001, first_name="User")

    practice = await _create_practice(
        db_session, master_auth["user"]["id"],
    )
    await _create_confirmed_booking(
        db_session, auth["user"]["id"], practice.id,
    )
    await db_session.commit()

    url = CHECKIN_URL.format(practice_id=practice.id)
    resp = await client.post(
        url,
        json={"mood": "high", "comment": "Feeling great"},
        headers=auth_headers(auth["session_token"]),
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["mood"] == "high"
    assert data["comment"] == "Feeling great"
    assert data["check_type"] == "pre"
    assert data["practice_id"] == str(practice.id)
    assert data["user_id"] == auth["user"]["id"]


# ===================================================================
# POST /practices/{id}/checkin -- upsert (update existing)
# ===================================================================


@pytest.mark.asyncio
async def test_checkin_upsert_update(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Second POST updates existing check-in, same id."""
    master_auth = await _make_verified_master(
        client, db_session, telegram_id=85902,
    )
    auth = await login_user(client, telegram_id=85002, first_name="User2")

    practice = await _create_practice(
        db_session, master_auth["user"]["id"],
    )
    await _create_confirmed_booking(
        db_session, auth["user"]["id"], practice.id,
    )
    await db_session.commit()

    url = CHECKIN_URL.format(practice_id=practice.id)
    headers = auth_headers(auth["session_token"])

    # First check-in.
    resp1 = await client.post(
        url, json={"mood": "low"}, headers=headers,
    )
    assert resp1.status_code == 200
    checkin_id = resp1.json()["id"]

    # Update check-in.
    resp2 = await client.post(
        url, json={"mood": "high", "comment": "Changed my mind"},
        headers=headers,
    )
    assert resp2.status_code == 200
    assert resp2.json()["id"] == checkin_id  # Same record.
    assert resp2.json()["mood"] == "high"
    assert resp2.json()["comment"] == "Changed my mind"


# ===================================================================
# POST /practices/{id}/checkin -- no confirmed booking (404)
# ===================================================================


@pytest.mark.asyncio
async def test_checkin_no_booking(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """No confirmed booking for this practice: 404."""
    master_auth = await _make_verified_master(
        client, db_session, telegram_id=85903,
    )
    auth = await login_user(client, telegram_id=85003, first_name="User3")

    practice = await _create_practice(
        db_session, master_auth["user"]["id"],
    )
    await db_session.commit()

    url = CHECKIN_URL.format(practice_id=practice.id)
    resp = await client.post(
        url,
        json={"mood": "mid"},
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 404


# ===================================================================
# POST /practices/{id}/checkin -- window too early (400)
# ===================================================================


@pytest.mark.asyncio
async def test_checkin_window_too_early(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Practice too far in the future: 400."""
    master_auth = await _make_verified_master(
        client, db_session, telegram_id=85904,
    )
    auth = await login_user(client, telegram_id=85004, first_name="User4")

    # Practice 48 hours from now -- outside default 3h window.
    practice = await _create_practice(
        db_session,
        master_auth["user"]["id"],
        scheduled_at=datetime.now(UTC) + timedelta(hours=48),
    )
    await _create_confirmed_booking(
        db_session, auth["user"]["id"], practice.id,
    )
    await db_session.commit()

    url = CHECKIN_URL.format(practice_id=practice.id)
    resp = await client.post(
        url,
        json={"mood": "mid"},
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 400


# ===================================================================
# POST /practices/{id}/checkin -- window closed (400)
# ===================================================================


@pytest.mark.asyncio
async def test_checkin_window_closed(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Practice already started: 400."""
    master_auth = await _make_verified_master(
        client, db_session, telegram_id=85905,
    )
    auth = await login_user(client, telegram_id=85005, first_name="User5")

    # Practice 1 hour in the past.
    practice = await _create_practice(
        db_session,
        master_auth["user"]["id"],
        scheduled_at=datetime.now(UTC) - timedelta(hours=1),
    )
    await _create_confirmed_booking(
        db_session, auth["user"]["id"], practice.id,
    )
    await db_session.commit()

    url = CHECKIN_URL.format(practice_id=practice.id)
    resp = await client.post(
        url,
        json={"mood": "mid"},
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 400


# ===================================================================
# POST /practices/{id}/checkin -- no auth (401)
# ===================================================================


@pytest.mark.asyncio
async def test_checkin_no_auth(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """No Authorization header: 401."""
    url = CHECKIN_URL.format(practice_id=uuid4())
    resp = await client.post(url, json={"mood": "mid"})
    assert resp.status_code == 401


# ===================================================================
# POST /practices/{id}/checkin -- invalid mood (422)
# ===================================================================


@pytest.mark.asyncio
async def test_checkin_invalid_mood(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Invalid mood value: 422."""
    auth = await login_user(client, telegram_id=85006, first_name="User6")
    url = CHECKIN_URL.format(practice_id=uuid4())
    resp = await client.post(
        url,
        json={"mood": "super_happy"},
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 422


# ===================================================================
# POST /practices/{id}/checkin -- comment too long (422)
# ===================================================================


@pytest.mark.asyncio
async def test_checkin_comment_too_long(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Comment exceeds 1000 chars: 422."""
    auth = await login_user(client, telegram_id=85007, first_name="User7")
    url = CHECKIN_URL.format(practice_id=uuid4())
    resp = await client.post(
        url,
        json={"mood": "mid", "comment": "x" * 1001},
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 422


# ===================================================================
# POST /practices/{id}/checkin -- mood without comment (ok)
# ===================================================================


@pytest.mark.asyncio
async def test_checkin_no_comment(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Mood only, no comment: 200, comment=null."""
    master_auth = await _make_verified_master(
        client, db_session, telegram_id=85906,
    )
    auth = await login_user(client, telegram_id=85008, first_name="User8")

    practice = await _create_practice(
        db_session, master_auth["user"]["id"],
    )
    await _create_confirmed_booking(
        db_session, auth["user"]["id"], practice.id,
    )
    await db_session.commit()

    url = CHECKIN_URL.format(practice_id=practice.id)
    resp = await client.post(
        url,
        json={"mood": "low"},
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 200
    assert resp.json()["comment"] is None


# ===================================================================
# GET /users/me/checkins -- empty list
# ===================================================================


@pytest.mark.asyncio
async def test_list_checkins_empty(
    client: AsyncClient,
) -> None:
    """No check-ins: empty list with total=0."""
    auth = await login_user(client, telegram_id=85009, first_name="User9")

    resp = await client.get(
        MY_CHECKINS_URL,
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0


# ===================================================================
# GET /users/me/checkins -- with data + pagination
# ===================================================================


@pytest.mark.asyncio
async def test_list_checkins_with_pagination(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """List check-ins with pagination (limit=1)."""
    master_auth = await _make_verified_master(
        client, db_session, telegram_id=85907,
    )
    auth = await login_user(client, telegram_id=85010, first_name="User10")
    headers = auth_headers(auth["session_token"])

    # Create 2 practices + bookings + check-ins.
    for i in range(2):
        practice = await _create_practice(
            db_session,
            master_auth["user"]["id"],
            scheduled_at=datetime.now(UTC) + timedelta(hours=2, minutes=i),
        )
        await _create_confirmed_booking(
            db_session, auth["user"]["id"], practice.id,
        )
        await db_session.commit()

        url = CHECKIN_URL.format(practice_id=practice.id)
        resp = await client.post(
            url, json={"mood": "mid"}, headers=headers,
        )
        assert resp.status_code == 200

    # Page 1.
    resp = await client.get(
        f"{MY_CHECKINS_URL}?limit=1&offset=0",
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 1
    assert data["total"] == 2

    # Page 2.
    resp2 = await client.get(
        f"{MY_CHECKINS_URL}?limit=1&offset=1",
        headers=headers,
    )
    assert resp2.status_code == 200
    assert len(resp2.json()["items"]) == 1


# ===================================================================
# GET /users/me/checkins -- filter by practice_id
# ===================================================================


@pytest.mark.asyncio
async def test_list_checkins_filter_practice(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Filter check-ins by practice_id."""
    master_auth = await _make_verified_master(
        client, db_session, telegram_id=85908,
    )
    auth = await login_user(client, telegram_id=85011, first_name="User11")
    headers = auth_headers(auth["session_token"])

    practices = []
    for i in range(2):
        p = await _create_practice(
            db_session,
            master_auth["user"]["id"],
            scheduled_at=datetime.now(UTC) + timedelta(hours=2, minutes=i),
        )
        await _create_confirmed_booking(
            db_session, auth["user"]["id"], p.id,
        )
        practices.append(p)

    await db_session.commit()

    # Check in to both.
    for p in practices:
        url = CHECKIN_URL.format(practice_id=p.id)
        await client.post(url, json={"mood": "high"}, headers=headers)

    # Filter by first practice.
    resp = await client.get(
        f"{MY_CHECKINS_URL}?practice_id={practices[0].id}",
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["practice_id"] == str(practices[0].id)


# ===================================================================
# GET /users/me/checkins -- no auth (401)
# ===================================================================


@pytest.mark.asyncio
async def test_list_checkins_no_auth(
    client: AsyncClient,
) -> None:
    """No Authorization header: 401."""
    resp = await client.get(MY_CHECKINS_URL)
    assert resp.status_code == 401
