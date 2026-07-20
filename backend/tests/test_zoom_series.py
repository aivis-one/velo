# =============================================================================
# Tests: Zoom Meeting Creation for Series Children (E21, closing the series
# hole -- ПРОМТ №520)
# =============================================================================
#
# telegram_id range: 79100-79199 (own band, no overlap with test_zoom_lifecycle
# [79000-79099] or test_zoom_registrants [79200-79299]).
#
# ⚠ BACKEND-ONLY, UNPROVEN LOCALLY -- see test_zoom_lifecycle.py's module
# docstring for the exact local blocker (pre-existing stray key in
# backend/.env, observed this session, not touched). Same situation here:
# written to be read, collection-checked, never executed.
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
from app.modules.zoom.models import ZoomMeeting, ZoomMeetingStatus
from app.modules.zoom.zoom_client import ZoomAPIError
from tests.helpers import auth_headers, login_user

PRACTICES_URL = "/api/v1/practices"

_TID_RANGE = "SELECT id FROM users WHERE telegram_id BETWEEN 79100 AND 79199"
_MASTER_RANGE = "SELECT id FROM users WHERE telegram_id BETWEEN 79100 AND 79120"

_CLEANUP_QUERIES = [
    text(
        "DELETE FROM zoom_meetings WHERE practice_id IN "
        "(SELECT id FROM practices WHERE master_id IN (" + _MASTER_RANGE + "))"
    ),
    text("DELETE FROM practices WHERE master_id IN (" + _MASTER_RANGE + ")"),
    text("DELETE FROM master_profiles WHERE user_id IN (" + _TID_RANGE + ")"),
    text(
        "UPDATE users SET role = 'user' "
        "WHERE telegram_id BETWEEN 79100 AND 79199"
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


async def _make_verified_master(
    client: AsyncClient, db_session: AsyncSession, telegram_id: int = 79101,
) -> dict:
    user_data = await login_user(
        client, telegram_id=telegram_id, first_name="SeriesMaster",
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


def _series_body(recurrence: dict) -> dict:
    return {
        "practice_type": "series",
        "direction": "meditation",
        "difficulty": "beginner",
        "title": "Zoom Series Test",
        "scheduled_at": (
            datetime.now(timezone.utc) + timedelta(days=8)
        ).isoformat(),
        "duration_minutes": 60,
        "timezone": "UTC",
        "is_free": True,
        "price_cents": 0,
        "currency": "eur",
        "recurrence": recurrence,
    }


@pytest.mark.asyncio
async def test_series_publish_creates_one_meeting_per_child_despite_one_failure(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """A series generating N children produces N meetings (root + children,
    each with its own ZoomMeeting row), and a Zoom failure on ONE child
    does not abort generation of the others.

    Catches: the series hole itself (children never getting a meeting at
    all) reappearing, AND a naive implementation that lets one child's
    Zoom exception propagate and kill the whole generation loop -- exactly
    the "series generation must never fail because Zoom failed" posture
    ПРОМТ №520 requires.
    """
    master = await _make_verified_master(client, db_session)

    # after_count=4 -> root + 3 children (daily).
    recurrence = {"period": "daily", "end": "after_count", "count": 4}
    create_resp = await client.post(
        PRACTICES_URL,
        json=_series_body(recurrence),
        headers=auth_headers(master["session_token"]),
    )
    assert create_resp.status_code == 201, create_resp.text
    root_id = create_resp.json()["id"]

    # Fail the 2nd create_meeting call (root succeeds via stub, child #1
    # fails, children #2 and #3 succeed via stub again) -- proves both
    # "one failure doesn't abort the rest" AND "the root itself still
    # succeeds independently of any child".
    call_count = {"n": 0}
    real_create_meeting = None

    async def _flaky_create_meeting(**kwargs):
        call_count["n"] += 1
        if call_count["n"] == 2:
            raise ZoomAPIError("simulated outage", status_code=500, body="down")
        # Delegate to the real (stub-mode) implementation for every other call.
        from app.modules.zoom.zoom_client import create_meeting as real_fn
        return await real_fn(**kwargs)

    with patch(
        "app.modules.zoom.service.create_meeting", side_effect=_flaky_create_meeting,
    ):
        patch_resp = await client.patch(
            f"{PRACTICES_URL}/{root_id}",
            json={"status": "scheduled"},
            headers=auth_headers(master["session_token"]),
        )
    assert patch_resp.status_code == 200, patch_resp.text
    assert patch_resp.json()["status"] == "scheduled"

    # Root + 3 children = 4 practices total.
    all_practice_ids = (
        await db_session.execute(
            select(Practice.id).where(
                (Practice.id == UUID(root_id))
                | (Practice.parent_practice_id == UUID(root_id))
            )
        )
    ).scalars().all()
    assert len(all_practice_ids) == 4, "expected root + 3 generated children"

    zoom_meetings = (
        await db_session.execute(
            select(ZoomMeeting).where(ZoomMeeting.practice_id.in_(all_practice_ids))
        )
    ).scalars().all()

    # ONE ZoomMeeting row per practice -- the series hole is closed.
    assert len(zoom_meetings) == 4, (
        "every practice in the series (root + each child) must get its own "
        "ZoomMeeting row, including the one Zoom failed on"
    )

    statuses = [m.status for m in zoom_meetings]
    assert statuses.count(ZoomMeetingStatus.CREATE_FAILED.value) == 1, (
        "exactly the one simulated failure should be create_failed"
    )
    assert statuses.count(ZoomMeetingStatus.ACTIVE.value) == 3, (
        "the other three (root + 2 children) must have succeeded despite "
        "the failure in between -- generation must not abort on one Zoom error"
    )

    failed_row = next(
        m for m in zoom_meetings if m.status == ZoomMeetingStatus.CREATE_FAILED.value
    )
    assert failed_row.last_sync_error is not None
    assert "500" in failed_row.last_sync_error
