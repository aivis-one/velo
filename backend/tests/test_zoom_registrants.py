# =============================================================================
# Tests: Zoom Registrant Lifecycle (E21 step E -- ПРОМТ №520)
# =============================================================================
#
# telegram_id range: 79200-79299
#   79201-79210: masters
#   79220-79240: regular users (bookers)
#
# ⚠ BACKEND-ONLY, UNPROVEN LOCALLY -- see test_zoom_lifecycle.py's module
# docstring for the exact local blocker (pre-existing stray key in
# backend/.env, observed this session, not touched). Written to be read,
# collection-checked, never executed.
# =============================================================================

from collections.abc import AsyncGenerator
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.masters.models import MasterProfile
from app.modules.practices.models import Practice
from app.modules.users.models import User, UserRole
from app.modules.zoom.models import (
    ZoomMeeting,
    ZoomMeetingStatus,
    ZoomRegistrant,
    ZoomRegistrantRole,
    ZoomRegistrantStatus,
)
from app.modules.zoom.service import ensure_host_registrant
from app.modules.zoom.zoom_client import ZoomAPIError
from tests.helpers import auth_headers, login_user

PRACTICES_URL = "/api/v1/practices"
BOOKINGS_URL = "/api/v1/bookings"

_TID_RANGE = "SELECT id FROM users WHERE telegram_id BETWEEN 79200 AND 79299"
_MASTER_RANGE = "SELECT id FROM users WHERE telegram_id BETWEEN 79200 AND 79210"

_CLEANUP_QUERIES = [
    text(
        "DELETE FROM zoom_registrants WHERE zoom_meeting_id IN "
        "(SELECT id FROM zoom_meetings WHERE practice_id IN "
        "(SELECT id FROM practices WHERE master_id IN (" + _MASTER_RANGE + ")))"
    ),
    text(
        "DELETE FROM zoom_meetings WHERE practice_id IN "
        "(SELECT id FROM practices WHERE master_id IN (" + _MASTER_RANGE + "))"
    ),
    text("DELETE FROM bookings WHERE user_id IN (" + _TID_RANGE + ")"),
    text("DELETE FROM practices WHERE master_id IN (" + _MASTER_RANGE + ")"),
    text("DELETE FROM master_profiles WHERE user_id IN (" + _TID_RANGE + ")"),
    text(
        "UPDATE users SET role = 'user' "
        "WHERE telegram_id BETWEEN 79200 AND 79299"
    ),
]


async def _full_cleanup(db_session: AsyncSession) -> None:
    for stmt in _CLEANUP_QUERIES:
        await db_session.execute(stmt)
    await db_session.commit()


@pytest.fixture(autouse=True)
async def cleanup(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    await _full_cleanup(db_session)
    yield
    await _full_cleanup(db_session)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _make_verified_master(
    client: AsyncClient, db_session: AsyncSession, telegram_id: int = 79201,
) -> dict:
    user_data = await login_user(
        client, telegram_id=telegram_id, first_name="RegMaster",
    )
    user_id = user_data["user"]["id"]
    user = (
        await db_session.execute(select(User).where(User.id == user_id))
    ).scalar_one()
    user.role = UserRole.MASTER.value
    await db_session.flush()
    db_session.add(
        MasterProfile(
            user_id=UUID(user_id), data={"account": {"status": "verified"}},
        )
    )
    await db_session.commit()
    return user_data


async def _create_and_publish_practice(
    client: AsyncClient,
    master_data: dict,
    *,
    fail_zoom_create: bool = False,
) -> str:
    body = {
        "practice_type": "live",
        "direction": "meditation",
        "difficulty": "beginner",
        "title": "Zoom Registrant Test Practice",
        "scheduled_at": (
            datetime.now(timezone.utc) + timedelta(hours=168)
        ).isoformat(),
        "duration_minutes": 60,
        "timezone": "UTC",
        "is_free": True,
        "price_cents": 0,
        "currency": "eur",
    }
    resp = await client.post(
        PRACTICES_URL, json=body, headers=auth_headers(master_data["session_token"]),
    )
    assert resp.status_code == 201
    practice_id = resp.json()["id"]

    if fail_zoom_create:
        with patch(
            "app.modules.zoom.service.create_meeting",
            side_effect=ZoomAPIError("simulated outage", status_code=500, body="down"),
        ):
            resp = await client.patch(
                f"{PRACTICES_URL}/{practice_id}",
                json={"status": "scheduled"},
                headers=auth_headers(master_data["session_token"]),
            )
    else:
        resp = await client.patch(
            f"{PRACTICES_URL}/{practice_id}",
            json={"status": "scheduled"},
            headers=auth_headers(master_data["session_token"]),
        )
    assert resp.status_code == 200
    return practice_id


async def _book(client: AsyncClient, user_data: dict, practice_id: str) -> dict:
    return await client.post(
        BOOKINGS_URL,
        json={"practice_id": practice_id},
        headers=auth_headers(user_data["session_token"]),
    )


async def _zoom_registrant_for_booking(
    db_session: AsyncSession, booking_id: str,
) -> ZoomRegistrant | None:
    return (
        await db_session.execute(
            select(ZoomRegistrant).where(ZoomRegistrant.booking_id == UUID(booking_id))
        )
    ).scalar_one_or_none()


# ===================================================================
# 1. Booking succeeds when the meeting isn't active yet -- registrant queued
# ===================================================================


@pytest.mark.asyncio
async def test_booking_succeeds_when_meeting_not_active_registrant_queued(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Publish with a failed Zoom meeting create (meeting stays
    create_failed, never active) -- booking still returns 2xx, and the
    registrant row exists with status=pending (queued for the retry
    poller), never lost.

    Catches: booking creation silently skipping the registrant row instead
    of queuing it, which would make the row unrecoverable once the meeting
    eventually goes active (nothing left to retry).
    """
    master = await _make_verified_master(client, db_session, telegram_id=79201)
    practice_id = await _create_and_publish_practice(
        client, master, fail_zoom_create=True,
    )

    zoom_meeting = (
        await db_session.execute(
            select(ZoomMeeting).where(ZoomMeeting.practice_id == UUID(practice_id))
        )
    ).scalar_one()
    assert zoom_meeting.status == ZoomMeetingStatus.CREATE_FAILED.value

    student = await login_user(client, telegram_id=79221, first_name="Student1")
    resp = await _book(client, student, practice_id)
    assert resp.status_code == 201, resp.text
    booking_id = resp.json()["id"]

    registrant = await _zoom_registrant_for_booking(db_session, booking_id)
    assert registrant is not None, "registrant row must exist, queued not lost"
    assert registrant.status == ZoomRegistrantStatus.PENDING.value
    assert registrant.zoom_registrant_id is None
    assert registrant.role == ZoomRegistrantRole.STUDENT.value


# ===================================================================
# 2. Booking succeeds when the Zoom registrant call itself raises
# ===================================================================


@pytest.mark.asyncio
async def test_booking_succeeds_when_zoom_registrant_call_raises(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Meeting IS active, but create_registrant raises -- booking still
    returns 2xx, registrant row lands create_failed for the retry poller.
    """
    master = await _make_verified_master(client, db_session, telegram_id=79202)
    practice_id = await _create_and_publish_practice(client, master)

    student = await login_user(client, telegram_id=79222, first_name="Student2")
    with patch(
        "app.modules.zoom.service.create_registrant",
        side_effect=ZoomAPIError("simulated failure", status_code=400, body="bad"),
    ):
        resp = await _book(client, student, practice_id)
    assert resp.status_code == 201, resp.text
    booking_id = resp.json()["id"]

    registrant = await _zoom_registrant_for_booking(db_session, booking_id)
    assert registrant is not None
    assert registrant.status == ZoomRegistrantStatus.CREATE_FAILED.value
    assert registrant.last_sync_error is not None
    assert "400" in registrant.last_sync_error


# ===================================================================
# 3. Host registrant created exactly once, no booking_id
# ===================================================================


@pytest.mark.asyncio
async def test_host_registrant_created_once_no_booking_id(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Publishing creates exactly one role='host' registrant with
    booking_id=NULL. Calling ensure_host_registrant again for the same
    meeting is a no-op (idempotent) -- this is what guarantees "exactly
    once" across both the initial-success path and a later retry-poller
    success path for the same meeting.
    """
    master = await _make_verified_master(client, db_session, telegram_id=79203)
    practice_id = await _create_and_publish_practice(client, master)

    zoom_meeting = (
        await db_session.execute(
            select(ZoomMeeting).where(ZoomMeeting.practice_id == UUID(practice_id))
        )
    ).scalar_one()
    assert zoom_meeting.status == ZoomMeetingStatus.ACTIVE.value

    host_rows = (
        await db_session.execute(
            select(ZoomRegistrant).where(
                ZoomRegistrant.zoom_meeting_id == zoom_meeting.id,
                ZoomRegistrant.role == ZoomRegistrantRole.HOST.value,
            )
        )
    ).scalars().all()
    assert len(host_rows) == 1
    assert host_rows[0].booking_id is None
    assert host_rows[0].user_id == UUID(master["user"]["id"])

    # Idempotency: calling it again must not create a second host row (the
    # mechanism a later successful retry relies on for "exactly once").
    practice = await db_session.get(Practice, UUID(practice_id))
    await ensure_host_registrant(zoom_meeting, practice, db_session)
    await db_session.commit()

    host_rows_after = (
        await db_session.execute(
            select(ZoomRegistrant).where(
                ZoomRegistrant.zoom_meeting_id == zoom_meeting.id,
                ZoomRegistrant.role == ZoomRegistrantRole.HOST.value,
            )
        )
    ).scalars().all()
    assert len(host_rows_after) == 1, "must stay exactly one host registrant"


# ===================================================================
# 4. Cancelling a booking marks our row cancelled even if Zoom fails
# ===================================================================


@pytest.mark.asyncio
async def test_cancel_booking_marks_registrant_cancelled_even_when_zoom_fails(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Our row's status is the sole authority (E21 design): even when the
    Zoom registrant-status-update call raises, cancelling the booking still
    marks our ZoomRegistrant row cancelled and the booking cancel itself
    still succeeds.
    """
    master = await _make_verified_master(client, db_session, telegram_id=79204)
    practice_id = await _create_and_publish_practice(client, master)

    student = await login_user(client, telegram_id=79224, first_name="Student4")
    book_resp = await _book(client, student, practice_id)
    assert book_resp.status_code == 201
    booking_id = book_resp.json()["id"]

    registrant = await _zoom_registrant_for_booking(db_session, booking_id)
    assert registrant is not None
    assert registrant.status == ZoomRegistrantStatus.REGISTERED.value
    assert registrant.zoom_registrant_id is not None

    with patch(
        "app.modules.zoom.service.update_registrant_status",
        side_effect=ZoomAPIError("simulated failure", status_code=500, body="down"),
    ):
        cancel_resp = await client.delete(
            f"{BOOKINGS_URL}/{booking_id}",
            headers=auth_headers(student["session_token"]),
        )
    assert cancel_resp.status_code == 200, cancel_resp.text

    await db_session.refresh(registrant)
    assert registrant.status == ZoomRegistrantStatus.CANCELLED.value
