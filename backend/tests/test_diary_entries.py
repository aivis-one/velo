# =============================================================================
# VELO Backend -- Tests: Diary Entries (Phase 8.3)
# =============================================================================
#
# telegram_id range: 87000-87999
#
# Coverage:
#   - POST /diary (create with/without practice_id, mood, title)
#   - GET /diary (list, pagination, filters: practice_id, mood, date range)
#   - GET /diary/{id} (own entry, other user's entry)
#   - PATCH /diary/{id} (update content, mood, clear fields, other user)
#   - DELETE /diary/{id} (own entry, other user's entry)
#   - Practice link validation (practice exists, user has booking)
#   - Input validation (content too long, title too long, invalid mood)
#   - Auth checks (401)
# =============================================================================

from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.bookings.models import Booking, BookingStatus
from app.modules.diary.models import DiaryEntry
from app.modules.masters.models import MasterProfile
from app.modules.practices.models import Practice, PracticeStatus, PracticeType
from app.modules.users.models import User, UserRole
from tests.helpers import auth_headers, login_user

DIARY_URL = "/api/v1/diary"

# telegram_id range for this test file.
_TID_MIN = 87000
_TID_MAX = 87999


# ===================================================================
# Cleanup
# ===================================================================


@pytest.fixture(autouse=True)
async def cleanup(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    """Clean test data before/after each test in FK-safe order."""
    await _do_cleanup(db_session)
    yield
    await _do_cleanup(db_session)


async def _do_cleanup(session: AsyncSession) -> None:
    """Delete all test entities for telegram_id 87000-87999."""
    await session.rollback()

    user_ids_subq = (
        select(User.id).where(
            User.telegram_id.between(_TID_MIN, _TID_MAX),
        )
    )

    # 1. diary_entries (FK -> users, practices).
    await session.execute(
        DiaryEntry.__table__.delete().where(
            DiaryEntry.user_id.in_(user_ids_subq),
        )
    )
    # 2. audit_logs for our users.
    from app.core.audit import AuditLog
    await session.execute(
        AuditLog.__table__.delete().where(
            AuditLog.actor_id.in_(user_ids_subq),
        )
    )
    # 3. bookings (FK -> practices, users).
    await session.execute(
        Booking.__table__.delete().where(
            Booking.user_id.in_(user_ids_subq),
        )
    )
    # 4. practices (FK -> master_profiles).
    await session.execute(
        Practice.__table__.delete().where(
            Practice.master_id.in_(user_ids_subq),
        )
    )
    # 5. master_profiles (FK -> users).
    await session.execute(
        MasterProfile.__table__.delete().where(
            MasterProfile.user_id.in_(user_ids_subq),
        )
    )
    # 6. users.
    await session.execute(
        User.__table__.delete().where(
            User.telegram_id.between(_TID_MIN, _TID_MAX),
        )
    )
    await session.commit()


# ===================================================================
# Helpers
# ===================================================================


async def _make_verified_master(
    client: AsyncClient,
    db_session: AsyncSession,
    telegram_id: int = 87900,
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


async def _create_practice_with_booking(
    client: AsyncClient,
    db_session: AsyncSession,
    user_id: str,
    master_telegram_id: int = 87901,
) -> Practice:
    """Create a practice with a confirmed booking for the user."""
    master_auth = await _make_verified_master(
        client, db_session, telegram_id=master_telegram_id,
    )

    practice = Practice(
        master_id=master_auth["user"]["id"],
        title="Practice for Diary",
        description="Test practice",
        practice_type=PracticeType.LIVE.value,
        status=PracticeStatus.SCHEDULED.value,
        scheduled_at=datetime.now(UTC) + timedelta(hours=2),
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

    booking = Booking(
        practice_id=practice.id,
        user_id=user_id,
        status=BookingStatus.CONFIRMED.value,
    )
    db_session.add(booking)
    await db_session.flush()

    return practice


# ===================================================================
# POST /diary -- create success (minimal)
# ===================================================================


@pytest.mark.asyncio
async def test_create_entry_minimal(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Create entry with only content: 201."""
    auth = await login_user(client, telegram_id=87001, first_name="User1")

    resp = await client.post(
        DIARY_URL,
        json={"content": "Today was a good day."},
        headers=auth_headers(auth["session_token"]),
    )

    assert resp.status_code == 201
    data = resp.json()
    assert data["content"] == "Today was a good day."
    assert data["title"] is None
    assert data["mood"] is None
    assert data["practice_id"] is None
    assert data["user_id"] == auth["user"]["id"]


# ===================================================================
# POST /diary -- create success (full)
# ===================================================================


@pytest.mark.asyncio
async def test_create_entry_full(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Create entry with all fields: 201."""
    auth = await login_user(client, telegram_id=87002, first_name="User2")

    practice = await _create_practice_with_booking(
        client, db_session, auth["user"]["id"], master_telegram_id=87902,
    )
    await db_session.commit()

    resp = await client.post(
        DIARY_URL,
        json={
            "content": "Felt amazing after meditation.",
            "title": "Morning Reflection",
            "mood": 9,
            "practice_id": str(practice.id),
        },
        headers=auth_headers(auth["session_token"]),
    )

    assert resp.status_code == 201
    data = resp.json()
    assert data["content"] == "Felt amazing after meditation."
    assert data["title"] == "Morning Reflection"
    assert data["mood"] == 9
    assert data["practice_id"] == str(practice.id)


# ===================================================================
# POST /diary -- practice not found (404)
# ===================================================================


@pytest.mark.asyncio
async def test_create_entry_practice_not_found(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Practice ID does not exist: 404."""
    auth = await login_user(client, telegram_id=87003, first_name="User3")

    resp = await client.post(
        DIARY_URL,
        json={
            "content": "Some thoughts.",
            "practice_id": str(uuid4()),
        },
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 404


# ===================================================================
# POST /diary -- practice exists but no booking (400)
# ===================================================================


@pytest.mark.asyncio
async def test_create_entry_no_booking(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Practice exists but user has no booking: 400."""
    auth = await login_user(client, telegram_id=87004, first_name="User4")
    master_auth = await _make_verified_master(
        client, db_session, telegram_id=87903,
    )

    # Practice without booking for this user.
    practice = Practice(
        master_id=master_auth["user"]["id"],
        title="Unbooked Practice",
        description="No booking",
        practice_type=PracticeType.LIVE.value,
        status=PracticeStatus.SCHEDULED.value,
        scheduled_at=datetime.now(UTC) + timedelta(hours=2),
        duration_minutes=60,
        timezone="UTC",
        max_participants=20,
        current_participants=0,
        is_free=True,
        price_cents=0,
        currency="eur",
    )
    db_session.add(practice)
    await db_session.commit()

    resp = await client.post(
        DIARY_URL,
        json={
            "content": "Thoughts about unbooked practice.",
            "practice_id": str(practice.id),
        },
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 400


# ===================================================================
# POST /diary -- content too long (422)
# ===================================================================


@pytest.mark.asyncio
async def test_create_entry_content_too_long(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Content exceeds 10000 chars: 422."""
    auth = await login_user(client, telegram_id=87005, first_name="User5")

    resp = await client.post(
        DIARY_URL,
        json={"content": "x" * 10001},
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 422


# ===================================================================
# POST /diary -- title too long (422)
# ===================================================================


@pytest.mark.asyncio
async def test_create_entry_title_too_long(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Title exceeds 200 chars: 422."""
    auth = await login_user(client, telegram_id=87006, first_name="User6")

    resp = await client.post(
        DIARY_URL,
        json={"content": "Some text.", "title": "T" * 201},
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 422


# ===================================================================
# POST /diary -- invalid mood (422)
# ===================================================================


@pytest.mark.asyncio
async def test_create_entry_invalid_mood(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Invalid mood value: 422."""
    auth = await login_user(client, telegram_id=87007, first_name="User7")

    resp = await client.post(
        DIARY_URL,
        json={"content": "Text.", "mood": 11},
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 422


# ===================================================================
# POST /diary -- no auth (401)
# ===================================================================


@pytest.mark.asyncio
async def test_create_entry_no_auth(
    client: AsyncClient,
) -> None:
    """No auth: 401."""
    resp = await client.post(
        DIARY_URL,
        json={"content": "Hello."},
    )
    assert resp.status_code == 401


# ===================================================================
# GET /diary -- list success
# ===================================================================


@pytest.mark.asyncio
async def test_list_entries_success(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """List diary entries: returns paginated response."""
    auth = await login_user(client, telegram_id=87008, first_name="User8")
    headers = auth_headers(auth["session_token"])

    # Create 3 entries.
    for i in range(3):
        await client.post(
            DIARY_URL,
            json={"content": f"Entry number {i}"},
            headers=headers,
        )

    resp = await client.get(DIARY_URL, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3
    # Newest first.
    assert "Entry number 2" in data["items"][0]["content"]


# ===================================================================
# GET /diary -- filter by mood
# ===================================================================


@pytest.mark.asyncio
async def test_list_entries_filter_mood(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Filter diary entries by mood."""
    auth = await login_user(client, telegram_id=87009, first_name="User9")
    headers = auth_headers(auth["session_token"])

    await client.post(
        DIARY_URL,
        json={"content": "Happy day", "mood": 9},
        headers=headers,
    )
    await client.post(
        DIARY_URL,
        json={"content": "Rough day", "mood": 2},
        headers=headers,
    )

    resp = await client.get(
        f"{DIARY_URL}?mood=9",
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["mood"] == 9


# ===================================================================
# GET /diary -- pagination
# ===================================================================


@pytest.mark.asyncio
async def test_list_entries_pagination(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Pagination limit/offset works correctly."""
    auth = await login_user(client, telegram_id=87010, first_name="User10")
    headers = auth_headers(auth["session_token"])

    for i in range(5):
        await client.post(
            DIARY_URL,
            json={"content": f"Entry {i}"},
            headers=headers,
        )

    resp = await client.get(
        f"{DIARY_URL}?limit=2&offset=0",
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2

    resp2 = await client.get(
        f"{DIARY_URL}?limit=2&offset=4",
        headers=headers,
    )
    data2 = resp2.json()
    assert len(data2["items"]) == 1


# ===================================================================
# GET /diary/{id} -- success
# ===================================================================


@pytest.mark.asyncio
async def test_get_entry_success(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Get single entry by ID: 200."""
    auth = await login_user(client, telegram_id=87011, first_name="User11")
    headers = auth_headers(auth["session_token"])

    create_resp = await client.post(
        DIARY_URL,
        json={"content": "My private thoughts."},
        headers=headers,
    )
    entry_id = create_resp.json()["id"]

    resp = await client.get(
        f"{DIARY_URL}/{entry_id}",
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == entry_id
    assert resp.json()["content"] == "My private thoughts."


# ===================================================================
# GET /diary/{id} -- other user's entry (404, P-08)
# ===================================================================


@pytest.mark.asyncio
async def test_get_entry_other_user(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Access another user's entry: 404 (not 403, P-08)."""
    auth1 = await login_user(client, telegram_id=87012, first_name="User12")
    auth2 = await login_user(client, telegram_id=87013, first_name="User13")

    # User1 creates entry.
    create_resp = await client.post(
        DIARY_URL,
        json={"content": "User1's secret."},
        headers=auth_headers(auth1["session_token"]),
    )
    entry_id = create_resp.json()["id"]

    # User2 tries to read it.
    resp = await client.get(
        f"{DIARY_URL}/{entry_id}",
        headers=auth_headers(auth2["session_token"]),
    )
    assert resp.status_code == 404


# ===================================================================
# PATCH /diary/{id} -- update success
# ===================================================================


@pytest.mark.asyncio
async def test_update_entry_success(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Update content and mood: 200."""
    auth = await login_user(client, telegram_id=87014, first_name="User14")
    headers = auth_headers(auth["session_token"])

    create_resp = await client.post(
        DIARY_URL,
        json={"content": "Original text.", "mood": 2},
        headers=headers,
    )
    entry_id = create_resp.json()["id"]

    resp = await client.patch(
        f"{DIARY_URL}/{entry_id}",
        json={"content": "Updated text.", "mood": 9},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["content"] == "Updated text."
    assert data["mood"] == 9
    assert data["id"] == entry_id


# ===================================================================
# PATCH /diary/{id} -- clear nullable fields
# ===================================================================


@pytest.mark.asyncio
async def test_update_entry_clear_fields(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Clear mood and title via clear_* flags."""
    auth = await login_user(client, telegram_id=87015, first_name="User15")
    headers = auth_headers(auth["session_token"])

    create_resp = await client.post(
        DIARY_URL,
        json={
            "content": "Text with mood.",
            "title": "My Title",
            "mood": 6,
        },
        headers=headers,
    )
    entry_id = create_resp.json()["id"]

    resp = await client.patch(
        f"{DIARY_URL}/{entry_id}",
        json={"clear_mood": True, "clear_title": True},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["mood"] is None
    assert data["title"] is None
    assert data["content"] == "Text with mood."  # Unchanged.


# ===================================================================
# PATCH /diary/{id} -- other user's entry (404)
# ===================================================================


@pytest.mark.asyncio
async def test_update_entry_other_user(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Update another user's entry: 404."""
    auth1 = await login_user(client, telegram_id=87016, first_name="User16")
    auth2 = await login_user(client, telegram_id=87017, first_name="User17")

    create_resp = await client.post(
        DIARY_URL,
        json={"content": "User16's text."},
        headers=auth_headers(auth1["session_token"]),
    )
    entry_id = create_resp.json()["id"]

    resp = await client.patch(
        f"{DIARY_URL}/{entry_id}",
        json={"content": "Hacked!"},
        headers=auth_headers(auth2["session_token"]),
    )
    assert resp.status_code == 404


# ===================================================================
# DELETE /diary/{id} -- success
# ===================================================================


@pytest.mark.asyncio
async def test_delete_entry_success(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Delete own entry: 204, then GET returns 404."""
    auth = await login_user(client, telegram_id=87018, first_name="User18")
    headers = auth_headers(auth["session_token"])

    create_resp = await client.post(
        DIARY_URL,
        json={"content": "To be deleted."},
        headers=headers,
    )
    entry_id = create_resp.json()["id"]

    del_resp = await client.delete(
        f"{DIARY_URL}/{entry_id}",
        headers=headers,
    )
    assert del_resp.status_code == 204

    # Verify it's gone.
    get_resp = await client.get(
        f"{DIARY_URL}/{entry_id}",
        headers=headers,
    )
    assert get_resp.status_code == 404


# ===================================================================
# DELETE /diary/{id} -- other user's entry (404)
# ===================================================================


@pytest.mark.asyncio
async def test_delete_entry_other_user(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Delete another user's entry: 404."""
    auth1 = await login_user(client, telegram_id=87019, first_name="User19")
    auth2 = await login_user(client, telegram_id=87020, first_name="User20")

    create_resp = await client.post(
        DIARY_URL,
        json={"content": "User19's entry."},
        headers=auth_headers(auth1["session_token"]),
    )
    entry_id = create_resp.json()["id"]

    resp = await client.delete(
        f"{DIARY_URL}/{entry_id}",
        headers=auth_headers(auth2["session_token"]),
    )
    assert resp.status_code == 404


# ===================================================================
# GET /diary -- no auth (401)
# ===================================================================


@pytest.mark.asyncio
async def test_list_entries_no_auth(
    client: AsyncClient,
) -> None:
    """No auth: 401."""
    resp = await client.get(DIARY_URL)
    assert resp.status_code == 401
