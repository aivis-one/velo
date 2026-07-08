# =============================================================================
# VELO Backend -- Tests: Admin Participants (E1)
# =============================================================================
#
# telegram_id range: 97000-97999
#   97900     -- admin caller
#   97800     -- master (owns the practice used for practices_count)
#   97001+    -- participants
#
# The list is platform-wide (seed present), so list assertions check shape +
# pagination + that a specifically-created participant appears with the right
# practices_count, rather than exact totals. Window filters (new / active) are
# checked by pushing one participant's created_at / last_login_at into the
# previous month and asserting it drops out of the current-week window.
#
# Cleanup is explicit + FK-safe for the 97xxx range.
# =============================================================================

from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.bookings.models import Booking, BookingStatus
from app.modules.masters.models import MasterProfile
from app.modules.practices.models import Practice, PracticeStatus, PracticeType
from app.modules.users.models import User, UserRole
from tests.helpers import auth_headers, login_user

PARTICIPANTS_URL = "/api/v1/admin/participants"

_TID_MIN = 97000
_TID_MAX = 97999


# ===================================================================
# Cleanup (explicit, FK-safe)
# ===================================================================


@pytest.fixture(autouse=True)
async def cleanup(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    await _do_cleanup(db_session)
    yield
    await _do_cleanup(db_session)


async def _do_cleanup(session: AsyncSession) -> None:
    await session.rollback()
    subq = select(User.id).where(User.telegram_id.between(_TID_MIN, _TID_MAX))

    await session.execute(
        Booking.__table__.delete().where(Booking.user_id.in_(subq))
    )
    await session.execute(
        Practice.__table__.delete().where(Practice.master_id.in_(subq))
    )
    await session.execute(
        MasterProfile.__table__.delete().where(MasterProfile.user_id.in_(subq))
    )
    await session.execute(
        User.__table__.delete().where(
            User.telegram_id.between(_TID_MIN, _TID_MAX)
        )
    )
    await session.commit()


# ===================================================================
# Helpers
# ===================================================================


async def _make_admin(
    client: AsyncClient, db_session: AsyncSession, telegram_id: int = 97900,
) -> str:
    auth = await login_user(client, telegram_id=telegram_id, first_name="Admin")
    await db_session.execute(
        update(User)
        .where(User.id == auth["user"]["id"])
        .values(role=UserRole.ADMIN.value)
    )
    await db_session.flush()
    return auth["session_token"]


async def _make_master(
    client: AsyncClient, db_session: AsyncSession, telegram_id: int = 97800,
) -> str:
    auth = await login_user(client, telegram_id=telegram_id, first_name="Master")
    user_id = auth["user"]["id"]
    user = await db_session.get(User, user_id)
    user.role = UserRole.MASTER
    await db_session.flush()
    db_session.add(
        MasterProfile(
            user_id=user_id,
            data={
                "account": {"status": "verified"},
                "profile": {"display_name": "Master"},
            },
        )
    )
    await db_session.flush()
    return user_id


async def _make_user(
    client: AsyncClient, telegram_id: int, first_name: str = "P",
) -> str:
    auth = await login_user(
        client, telegram_id=telegram_id, first_name=first_name,
    )
    return auth["user"]["id"]


async def _create_practice(
    db_session: AsyncSession, master_id: str,
) -> Practice:
    practice = Practice(
        master_id=master_id,
        title="Participants Practice",
        description="x",
        practice_type=PracticeType.LIVE.value,
        status=PracticeStatus.SCHEDULED.value,
        scheduled_at=datetime.now(UTC) + timedelta(days=2),
        duration_minutes=60,
        timezone="UTC",
        max_participants=10,
        current_participants=0,
        is_free=True,
        price_cents=0,
        currency="eur",
        data={},
    )
    db_session.add(practice)
    await db_session.flush()
    return practice


# ===================================================================
# GET /admin/participants
# ===================================================================


@pytest.mark.asyncio
async def test_participants_requires_admin(
    client: AsyncClient, db_session: AsyncSession,
) -> None:
    """A non-admin caller is rejected."""
    auth = await login_user(client, telegram_id=97010, first_name="Plain")
    resp = await client.get(
        PARTICIPANTS_URL, headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_participants_list_shape_and_count(
    client: AsyncClient, db_session: AsyncSession,
) -> None:
    """Shape + pagination keys, and practices_count = non-cancelled bookings."""
    token = await _make_admin(client, db_session)
    master_id = await _make_master(client, db_session)
    practice = await _create_practice(db_session, master_id)

    user_id = await _make_user(client, 97001, "Booked")
    # One confirmed booking (counts) + one cancelled (must NOT count).
    db_session.add(
        Booking(
            practice_id=practice.id,
            user_id=user_id,
            status=BookingStatus.CONFIRMED.value,
        )
    )
    other = await _create_practice(db_session, master_id)
    db_session.add(
        Booking(
            practice_id=other.id,
            user_id=user_id,
            status=BookingStatus.CANCELLED.value,
        )
    )
    await db_session.commit()

    resp = await client.get(
        PARTICIPANTS_URL, params={"limit": 100}, headers=auth_headers(token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert {"items", "total", "limit", "offset"} == set(data.keys())
    assert data["items"], "expected at least one participant"
    item = data["items"][0]
    assert {
        "id", "name", "telegram_id", "avatar_url",
        "practices_count", "created_at", "last_login_at",
    } == set(item.keys())

    booked = next(p for p in data["items"] if p["id"] == user_id)
    assert booked["practices_count"] == 1  # cancelled booking excluded
    assert booked["telegram_id"] == 97001


@pytest.mark.asyncio
async def test_participants_filter_new_excludes_old(
    client: AsyncClient, db_session: AsyncSession,
) -> None:
    """filter=new (current week) includes a fresh user, excludes an old one.

    Asserts on the `new` filter directly (not `all`): `all` is ordered
    created_at DESC and page-capped, so a back-dated user legitimately falls
    off page 1 on a populated DB. `new` excludes the old user via its
    created_at >= week_start WHERE clause (page-position-independent), and the
    fresh user — being the newest row at request time — is always on page 1.
    """
    token = await _make_admin(client, db_session)
    fresh_id = await _make_user(client, 97002, "FreshJoin")  # created now
    old_id = await _make_user(client, 97004, "OldJoin")
    # Push created_at into the previous month -> outside the current-week window.
    await db_session.execute(
        update(User)
        .where(User.id == old_id)
        .values(created_at=datetime.now(UTC) - timedelta(days=40))
    )
    await db_session.commit()

    new_resp = await client.get(
        PARTICIPANTS_URL,
        params={"filter": "new", "period": "week", "limit": 100},
        headers=auth_headers(token),
    )
    assert new_resp.status_code == 200
    new_ids = {p["id"] for p in new_resp.json()["items"]}
    assert fresh_id in new_ids  # created this week -> included
    assert old_id not in new_ids  # created last month -> excluded by the window


@pytest.mark.asyncio
async def test_participants_filter_active_excludes_stale(
    client: AsyncClient, db_session: AsyncSession,
) -> None:
    """filter=active (current week) excludes a user last seen last month."""
    token = await _make_admin(client, db_session)
    stale_id = await _make_user(client, 97003, "Stale")
    # login_user set last_login_at=now; push it into the previous month.
    await db_session.execute(
        update(User)
        .where(User.id == stale_id)
        .values(last_login_at=datetime.now(UTC) - timedelta(days=40))
    )
    await db_session.commit()

    all_resp = await client.get(
        PARTICIPANTS_URL,
        params={"filter": "all", "limit": 100},
        headers=auth_headers(token),
    )
    active_resp = await client.get(
        PARTICIPANTS_URL,
        params={"filter": "active", "period": "week", "limit": 100},
        headers=auth_headers(token),
    )
    assert all_resp.status_code == 200 and active_resp.status_code == 200
    all_ids = {p["id"] for p in all_resp.json()["items"]}
    active_ids = {p["id"] for p in active_resp.json()["items"]}
    assert stale_id in all_ids
    assert stale_id not in active_ids
