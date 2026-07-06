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
from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.diary.models import CheckType, Checkin
from app.modules.notifications.models import (
    Notification,
    NotificationType,
    TargetType,
)
from app.modules.users.models import User, UserRole
from tests.helpers import auth_headers, login_user, full_cleanup_range, switch_self_to_master

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
    """Full ORM cleanup for telegram_id 63000-63999."""
    await full_cleanup_range(session, 63000, 63999, delete_users=False)
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
        "currency": "eur",
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
    update(User)
    .where(User.telegram_id == 63900)
    .values(role=UserRole.ADMIN.value)
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

    await switch_self_to_master(client, auth["session_token"])
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


async def _feedback_notifs(
    session: AsyncSession, pid: str,
) -> list[Notification]:
    """LEAVE_FEEDBACK notifications enqueued for this practice."""
    result = await session.execute(
        select(Notification).where(
            Notification.type == NotificationType.LEAVE_FEEDBACK.value,
            Notification.target_value == str(pid),
        )
    )
    return list(result.scalars().all())


@pytest.mark.asyncio
async def test_finalize_creates_feedback_notification(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Finalizing a practice with >=1 attendee enqueues a single
    LEAVE_FEEDBACK notification targeting the practice (the processor resolves
    the audience to confirmed/attended bookings)."""
    master = await _make_verified_master(client, db_session)
    pid = await _create_scheduled_practice(client, master)

    user_a = await _book_user(client, pid, telegram_id=63110)
    await client.post(
        f"{BOOKINGS_URL}/{user_a['booking_id']}/join",
        headers=auth_headers(user_a["session_token"]),
    )

    resp = await client.post(
        f"{PRACTICES_URL}/{pid}/finalize",
        headers=auth_headers(master["session_token"]),
    )
    assert resp.status_code == 200

    notifs = await _feedback_notifs(db_session, pid)
    assert len(notifs) == 1
    assert notifs[0].target_type == TargetType.PRACTICE.value


@pytest.mark.asyncio
async def test_finalize_no_attendees_no_feedback_notification(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """No attendee (booked but never joined -> no_show) -> no LEAVE_FEEDBACK
    notification (the attended_count > 0 guard)."""
    master = await _make_verified_master(client, db_session)
    pid = await _create_scheduled_practice(client, master)
    # Booked but never joins -> resolves to no_show on finalize.
    await _book_user(client, pid, telegram_id=63111)

    resp = await client.post(
        f"{PRACTICES_URL}/{pid}/finalize",
        headers=auth_headers(master["session_token"]),
    )
    assert resp.status_code == 200

    notifs = await _feedback_notifs(db_session, pid)
    assert len(notifs) == 0


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


# ===================================================================
# GET /practices/{id}/attendance -- enrichment (name/avatar + check-in)
# ===================================================================
#
# The attendance view is enriched for the master's prep screen: each item
# carries the participant's display name + avatar and their PRE check-in
# (mood + comment), if any. PRE check-ins are seeded directly via the ORM
# here: the public POST /checkin endpoint only accepts writes inside the
# time window (scheduled_at - checkin_window_hours .. scheduled_at), and the
# test practices are scheduled 7 days out, so the window is closed. Seeding
# the row directly is the same approach test_insights.py uses.


async def _seed_pre_checkin(
    session: AsyncSession,
    *,
    booking_id: str,
    practice_id: str,
    user_id: str,
    mood: int,
    comment: str | None,
) -> None:
    """Insert a PRE check-in row straight through the ORM (bypass window)."""
    session.add(
        Checkin(
            practice_id=UUID(practice_id),
            user_id=UUID(user_id),
            booking_id=UUID(booking_id),
            mood=mood,
            comment=comment,
            check_type=CheckType.PRE.value,
        )
    )
    await session.commit()


@pytest.mark.asyncio
async def test_attendance_includes_participant_name_and_avatar(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Each attendance item carries the participant's display name + avatar."""
    master = await _make_verified_master(client, db_session)
    pid = await _create_scheduled_practice(client, master)

    user = await _book_user(client, pid, telegram_id=63120)
    user_id = user["user"]["id"]

    # Set an avatar on the participant (login upserts avatar from Telegram
    # photo_url, which is None in tests, so we set it explicitly).
    avatar = "https://t.me/i/userpic/320/participant.jpg"
    await db_session.execute(
        update(User).where(User.id == UUID(user_id)).values(avatar_url=avatar)
    )
    await db_session.commit()

    resp = await client.get(
        f"{PRACTICES_URL}/{pid}/attendance",
        headers=auth_headers(master["session_token"]),
    )
    assert resp.status_code == 200
    item = resp.json()["items"][0]
    # login_user sends first_name="User" with no last_name.
    assert item["user_display_name"] == "User"
    assert item["user_avatar_url"] == avatar


@pytest.mark.asyncio
async def test_attendance_includes_checkin(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """A participant's PRE check-in (mood + comment) is exposed to the master."""
    master = await _make_verified_master(client, db_session)
    pid = await _create_scheduled_practice(client, master)

    user = await _book_user(client, pid, telegram_id=63121)
    await _seed_pre_checkin(
        db_session,
        booking_id=user["booking_id"],
        practice_id=pid,
        user_id=user["user"]["id"],
        mood=8,
        comment="болят колени, поберегите",
    )

    resp = await client.get(
        f"{PRACTICES_URL}/{pid}/attendance",
        headers=auth_headers(master["session_token"]),
    )
    assert resp.status_code == 200
    item = resp.json()["items"][0]
    assert item["checkin"] is not None
    assert item["checkin"]["mood"] == 8
    assert item["checkin"]["comment"] == "болят колени, поберегите"


@pytest.mark.asyncio
async def test_attendance_checkin_null_when_absent(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """checkin is null for a participant who left no PRE check-in."""
    master = await _make_verified_master(client, db_session)
    pid = await _create_scheduled_practice(client, master)

    await _book_user(client, pid, telegram_id=63122)

    resp = await client.get(
        f"{PRACTICES_URL}/{pid}/attendance",
        headers=auth_headers(master["session_token"]),
    )
    assert resp.status_code == 200
    item = resp.json()["items"][0]
    assert item["checkin"] is None


@pytest.mark.asyncio
async def test_attendance_checkin_comment_can_be_none(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """A check-in with mood but no comment surfaces mood + comment=None."""
    master = await _make_verified_master(client, db_session)
    pid = await _create_scheduled_practice(client, master)

    user = await _book_user(client, pid, telegram_id=63123)
    await _seed_pre_checkin(
        db_session,
        booking_id=user["booking_id"],
        practice_id=pid,
        user_id=user["user"]["id"],
        mood=5,
        comment=None,
    )

    resp = await client.get(
        f"{PRACTICES_URL}/{pid}/attendance",
        headers=auth_headers(master["session_token"]),
    )
    assert resp.status_code == 200
    item = resp.json()["items"][0]
    assert item["checkin"] is not None
    assert item["checkin"]["mood"] == 5
    assert item["checkin"]["comment"] is None


@pytest.mark.asyncio
async def test_attendance_enrichment_only_for_owner(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """A non-owner master gets 404 -- enriched check-ins are not exposed."""
    master = await _make_verified_master(client, db_session)
    pid = await _create_scheduled_practice(client, master)

    user = await _book_user(client, pid, telegram_id=63124)
    await _seed_pre_checkin(
        db_session,
        booking_id=user["booking_id"],
        practice_id=pid,
        user_id=user["user"]["id"],
        mood=9,
        comment="private note",
    )

    other_master = await _make_verified_master(
        client, db_session, telegram_id=63004,
    )
    resp = await client.get(
        f"{PRACTICES_URL}/{pid}/attendance",
        headers=auth_headers(other_master["session_token"]),
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_attendance_checkin_maps_to_correct_participant(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """With two participants, each check-in lands on the right item."""
    master = await _make_verified_master(client, db_session)
    pid = await _create_scheduled_practice(client, master)

    user_a = await _book_user(client, pid, telegram_id=63125)
    user_b = await _book_user(client, pid, telegram_id=63126)

    # Only user A leaves a check-in.
    await _seed_pre_checkin(
        db_session,
        booking_id=user_a["booking_id"],
        practice_id=pid,
        user_id=user_a["user"]["id"],
        mood=7,
        comment="A's note",
    )

    resp = await client.get(
        f"{PRACTICES_URL}/{pid}/attendance",
        headers=auth_headers(master["session_token"]),
    )
    assert resp.status_code == 200
    by_booking = {it["booking_id"]: it for it in resp.json()["items"]}

    a_item = by_booking[user_a["booking_id"]]
    b_item = by_booking[user_b["booking_id"]]

    assert a_item["checkin"] is not None
    assert a_item["checkin"]["comment"] == "A's note"
    assert b_item["checkin"] is None
