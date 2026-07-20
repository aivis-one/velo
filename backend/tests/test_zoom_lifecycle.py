# =============================================================================
# Tests: Zoom Meeting Lifecycle (E21 step D, ПРОМТ №519)
# =============================================================================
#
# telegram_id range: 79000-79099
#   79001-79020: masters
#   79021-79099: regular users (unused so far, reserved)
#
# ⚠ BACKEND-ONLY, UNPROVEN LOCALLY -- there is no docker/postgres available in
# this environment (per [[velo_testing]]). These tests were written to be
# read and were exercised via `pytest --collect-only` (import/collection
# succeeds) but never actually RUN against a live database -- collection
# success is NOT the same as passing. See the ГОТОВО report for exactly
# what was and wasn't observed.
#
# STUB MODE: no real Zoom credentials exist in any test environment, so
# settings.is_zoom_stub is True by default here and zoom_client._request()
# always returns deterministic fake data (see zoom_client.py) without a
# network call. Tests that need a FAILURE path mock zoom.service's
# zoom_client-level function directly (create_meeting / patch_meeting /
# list_registrants) to raise ZoomAPIError, since stub mode itself always
# "succeeds".
# =============================================================================

from collections.abc import AsyncGenerator
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.masters.models import MasterProfile
from app.modules.practices.models import PracticeStatus
from app.modules.users.models import User, UserRole
from app.modules.zoom.models import (
    ZoomMeeting,
    ZoomMeetingStatus,
    ZoomRegistrant,
    ZoomRegistrantRole,
)
from app.modules.zoom.retry_poller import _poll_cycle
from app.modules.zoom.zoom_client import ZoomAPIError
from tests.helpers import auth_headers, login_user

PRACTICES_URL = "/api/v1/practices"


# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

_TID_RANGE = "SELECT id FROM users WHERE telegram_id BETWEEN 79000 AND 79099"
_MASTER_RANGE = "SELECT id FROM users WHERE telegram_id BETWEEN 79000 AND 79020"

_CLEANUP_QUERIES = [
    text(
        "DELETE FROM zoom_attendance_segments WHERE zoom_meeting_id IN "
        "(SELECT id FROM zoom_meetings WHERE practice_id IN "
        "(SELECT id FROM practices WHERE master_id IN (" + _MASTER_RANGE + ")))"
    ),
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
        "WHERE telegram_id BETWEEN 79000 AND 79099"
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
    client: AsyncClient,
    db_session: AsyncSession,
    telegram_id: int = 79001,
) -> dict:
    user_data = await login_user(
        client, telegram_id=telegram_id, first_name="ZoomMaster",
    )
    user_id = user_data["user"]["id"]

    user = (
        await db_session.execute(select(User).where(User.id == user_id))
    ).scalar_one()
    user.role = UserRole.MASTER.value
    await db_session.flush()

    db_session.add(
        MasterProfile(
            user_id=UUID(user_id),
            data={"account": {"status": "verified"}},
        )
    )
    await db_session.commit()
    return user_data


async def _create_draft_practice(
    client: AsyncClient,
    master_data: dict,
    *,
    hours_ahead: int = 168,
) -> str:
    body = {
        "practice_type": "live",
        "direction": "meditation",
        "difficulty": "beginner",
        "title": "Zoom Lifecycle Test Practice",
        "scheduled_at": (
            datetime.now(timezone.utc) + timedelta(hours=hours_ahead)
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
    return resp.json()["id"]


async def _publish(client: AsyncClient, master_data: dict, practice_id: str):
    return await client.patch(
        f"{PRACTICES_URL}/{practice_id}",
        json={"status": "scheduled"},
        headers=auth_headers(master_data["session_token"]),
    )


async def _get_zoom_meeting(
    db_session: AsyncSession, practice_id: str,
) -> ZoomMeeting | None:
    return (
        await db_session.execute(
            select(ZoomMeeting).where(ZoomMeeting.practice_id == UUID(practice_id))
        )
    ).scalar_one_or_none()


# ===================================================================
# 1. Publish always succeeds -- Zoom failure recorded, never raised
# ===================================================================


@pytest.mark.asyncio
async def test_publish_succeeds_when_zoom_create_fails(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """PATCH draft->scheduled returns 2xx even when create_meeting raises.

    Catches: a practice becoming silently unpublishable because a third
    party (Zoom) is unreachable -- the exact failure the design forbids
    (E21 plan sec 2, confirmed ПРОМТ №519 amendment 2).
    """
    master = await _make_verified_master(client, db_session, telegram_id=79001)
    practice_id = await _create_draft_practice(client, master)

    with patch(
        "app.modules.zoom.service.create_meeting",
        side_effect=ZoomAPIError("simulated outage", status_code=503, body="down"),
    ):
        resp = await _publish(client, master, practice_id)

    assert resp.status_code == 200
    assert resp.json()["status"] == PracticeStatus.SCHEDULED.value

    zoom_meeting = await _get_zoom_meeting(db_session, practice_id)
    assert zoom_meeting is not None
    assert zoom_meeting.status == ZoomMeetingStatus.CREATE_FAILED.value
    assert zoom_meeting.last_sync_error is not None
    assert "503" in zoom_meeting.last_sync_error


@pytest.mark.asyncio
async def test_publish_records_active_meeting_on_zoom_success(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Sanity check for the happy path (stub mode succeeds by default):
    publish creates an ACTIVE ZoomMeeting row with Zoom's returned ids."""
    master = await _make_verified_master(client, db_session, telegram_id=79002)
    practice_id = await _create_draft_practice(client, master)

    resp = await _publish(client, master, practice_id)
    assert resp.status_code == 200

    zoom_meeting = await _get_zoom_meeting(db_session, practice_id)
    assert zoom_meeting is not None
    assert zoom_meeting.status == ZoomMeetingStatus.ACTIVE.value
    assert zoom_meeting.zoom_meeting_id is not None


# ===================================================================
# 2. Cancel a practice whose Zoom meeting never created -- no crash
# ===================================================================


@pytest.mark.asyncio
async def test_cancel_does_not_break_when_zoom_meeting_create_failed(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Cancelling a practice whose ZoomMeeting is still create_failed (Zoom
    was down at publish time) does not break the refund/cancel flow.

    Catches: delete_meeting_for_practice assuming an active meeting exists
    and raising / blocking cancellation when it doesn't.
    """
    master = await _make_verified_master(client, db_session, telegram_id=79003)
    practice_id = await _create_draft_practice(client, master)

    with patch(
        "app.modules.zoom.service.create_meeting",
        side_effect=ZoomAPIError("simulated outage", status_code=500, body="down"),
    ):
        resp = await _publish(client, master, practice_id)
    assert resp.status_code == 200

    zoom_meeting = await _get_zoom_meeting(db_session, practice_id)
    assert zoom_meeting.status == ZoomMeetingStatus.CREATE_FAILED.value

    with patch("app.modules.zoom.service.delete_meeting") as mock_delete:
        resp = await client.post(
            f"{PRACTICES_URL}/{practice_id}/cancel",
            json={},
            headers=auth_headers(master["session_token"]),
        )
        # delete_meeting must never be called for a non-active meeting.
        mock_delete.assert_not_called()

    assert resp.status_code == 200
    assert resp.json()["status"] == PracticeStatus.CANCELLED.value


# ===================================================================
# 3. Reschedule re-fetches and overwrites stored join links
# ===================================================================


@pytest.mark.asyncio
async def test_reschedule_refetches_and_overwrites_join_url(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """After a scheduled_at PATCH, stored registrant join_url is overwritten
    with whatever Zoom's registrant list currently returns.

    Catches: the self-healing reschedule design silently not running, which
    would leave a possibly-stale join_url in place with no way to tell
    (the whole reason this shape was chosen over resolving the survives-
    reschedule question up front -- E21 plan sec 2).
    """
    master = await _make_verified_master(client, db_session, telegram_id=79004)
    practice_id = await _create_draft_practice(client, master, hours_ahead=48)

    resp = await _publish(client, master, practice_id)
    assert resp.status_code == 200
    zoom_meeting = await _get_zoom_meeting(db_session, practice_id)
    assert zoom_meeting.status == ZoomMeetingStatus.ACTIVE.value

    # Seed one stored registrant with a known, stale join_url.
    stale_registrant = ZoomRegistrant(
        zoom_meeting_id=zoom_meeting.id,
        user_id=UUID(master["user"]["id"]),
        role=ZoomRegistrantRole.HOST.value,
        zoom_registrant_id="remote-reg-1",
        registration_email="stale@example.com",
        join_url="https://zoom.us/w/stale?tk=old",
    )
    db_session.add(stale_registrant)
    await db_session.commit()

    with (
        patch("app.modules.zoom.service.patch_meeting") as mock_patch,
        patch(
            "app.modules.zoom.service.list_registrants",
            return_value=[
                {
                    "registrant_id": "remote-reg-1",
                    "join_url": "https://zoom.us/w/fresh?tk=new",
                }
            ],
        ) as mock_list,
    ):
        resp = await client.patch(
            f"{PRACTICES_URL}/{practice_id}",
            json={
                "scheduled_at": (
                    datetime.now(timezone.utc) + timedelta(hours=72)
                ).isoformat(),
            },
            headers=auth_headers(master["session_token"]),
        )
        assert resp.status_code == 200
        mock_patch.assert_called_once()
        mock_list.assert_called_once()

    await db_session.refresh(stale_registrant)
    assert stale_registrant.join_url == "https://zoom.us/w/fresh?tk=new"


# ===================================================================
# 4. Retry poller respects its cap -- stays visibly failed past it
# ===================================================================


@pytest.mark.asyncio
async def test_retry_poller_stops_at_cap_and_stays_visibly_failed(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """A create_failed ZoomMeeting at retry_count == cap is never retried
    again -- status stays create_failed, last_sync_error still readable.

    Catches: unbounded retry (its own silent-failure mode per E21 plan) OR
    the row being silently abandoned with no trace of why once the cap is
    hit.
    """
    master = await _make_verified_master(client, db_session, telegram_id=79005)
    practice_id = await _create_draft_practice(client, master)

    cap = settings.zoom_meeting_create_max_retries

    zoom_meeting = ZoomMeeting(
        practice_id=UUID(practice_id),
        status=ZoomMeetingStatus.CREATE_FAILED.value,
        retry_count=cap,
        last_sync_error="pre-seeded: already at cap",
    )
    db_session.add(zoom_meeting)
    await db_session.commit()

    with patch("app.modules.zoom.retry_poller.create_meeting") as mock_create:
        work_done = await _poll_cycle()
        # At-cap row must not even be claimed, let alone retried.
        mock_create.assert_not_called()

    assert work_done is False

    await db_session.refresh(zoom_meeting)
    assert zoom_meeting.status == ZoomMeetingStatus.CREATE_FAILED.value
    assert zoom_meeting.retry_count == cap
    assert zoom_meeting.last_sync_error == "pre-seeded: already at cap"

    # Sanity: a row genuinely UNDER the cap IS claimed and retried, so the
    # above proves the cap is doing something rather than everything being
    # silently skipped.
    zoom_meeting.retry_count = cap - 1
    zoom_meeting.last_sync_error = "pre-seeded: one under cap"
    await db_session.commit()

    with patch(
        "app.modules.zoom.retry_poller.create_meeting",
        side_effect=ZoomAPIError("still down", status_code=503, body="down"),
    ) as mock_create:
        work_done = await _poll_cycle()
        mock_create.assert_called_once()

    assert work_done is True
    await db_session.refresh(zoom_meeting)
    assert zoom_meeting.retry_count == cap
    assert zoom_meeting.status == ZoomMeetingStatus.CREATE_FAILED.value
    assert "cap reached" in zoom_meeting.last_sync_error
    # Row cleanup happens via the autouse `cleanup` fixture (practice's
    # master is in the 79000-79020 range).
