# =============================================================================
# VELO Backend -- Tests: Admin Practices (E9 / 4c)
# =============================================================================
#
# telegram_id range: 94000-94999
#   94900     -- admin caller
#   94800     -- master (practice owner)
#   94001+    -- participants
#
# The list is platform-wide (seed present), so list assertions check scope
# invariants (every returned item matches the requested scope) + shape +
# pagination rather than exact totals. Detail is fetched by id -> isolated,
# so it carries exact field/roster assertions.
#
# Cleanup is explicit + FK-safe for the 94xxx range.
# =============================================================================

from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.bookings.models import Booking, BookingStatus
from app.modules.masters.models import MasterProfile
from app.modules.practices.models import Practice, PracticeStatus, PracticeType
from app.modules.users.models import User, UserRole
from tests.helpers import auth_headers, login_user

PRACTICES_URL = "/api/v1/admin/practices"
DETAIL_URL = "/api/v1/admin/practices/{practice_id}"

_TID_MIN = 94000
_TID_MAX = 94999


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
    from app.core.audit import AuditLog
    await session.execute(
        AuditLog.__table__.delete().where(AuditLog.actor_id.in_(subq))
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
    client: AsyncClient, db_session: AsyncSession, telegram_id: int = 94900,
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
    client: AsyncClient, db_session: AsyncSession, telegram_id: int = 94800,
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


async def _create_practice(
    db_session: AsyncSession,
    master_id: str,
    *,
    scheduled_at: datetime,
    status: str = PracticeStatus.SCHEDULED.value,
    max_participants: int | None = 10,
    direction: str | None = None,
) -> Practice:
    data = {"taxonomy": {"direction": direction}} if direction else {}
    practice = Practice(
        master_id=master_id,
        title="Admin Practice",
        description="x",
        practice_type=PracticeType.LIVE.value,
        status=status,
        scheduled_at=scheduled_at,
        duration_minutes=60,
        timezone="UTC",
        max_participants=max_participants,
        current_participants=0,
        is_free=True,
        price_cents=0,
        currency="eur",
        data=data,
    )
    db_session.add(practice)
    await db_session.flush()
    return practice


async def _book(
    client: AsyncClient,
    db_session: AsyncSession,
    practice: Practice,
    telegram_id: int,
    *,
    status: str = BookingStatus.CONFIRMED.value,
) -> None:
    auth = await login_user(
        client, telegram_id=telegram_id, first_name=f"P{telegram_id}",
    )
    db_session.add(
        Booking(
            practice_id=practice.id,
            user_id=auth["user"]["id"],
            status=status,
        )
    )
    await db_session.flush()


# ===================================================================
# GET /admin/practices -- list
# ===================================================================


@pytest.mark.asyncio
async def test_practices_list_shape(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """List returns the paginated shape; every item has a temporal status."""
    token = await _make_admin(client, db_session)
    master_id = await _make_master(client, db_session)
    await _create_practice(
        db_session, master_id, scheduled_at=datetime.now(UTC) + timedelta(days=2),
    )
    await _create_practice(
        db_session, master_id,
        scheduled_at=datetime.now(UTC) - timedelta(days=2),
        status=PracticeStatus.COMPLETED.value,
    )
    await db_session.commit()

    resp = await client.get(PRACTICES_URL, headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    assert {"items", "total", "limit", "offset"} <= set(data.keys())
    assert data["total"] >= 2
    assert data["items"], "expected at least one practice"
    item = data["items"][0]
    assert {
        "id", "title", "direction", "master_name", "master_verified",
        "scheduled_at", "duration_minutes", "booked", "capacity", "status",
        "timezone",
    } == set(item.keys())
    assert all(it["status"] in ("upcoming", "past") for it in data["items"])


@pytest.mark.asyncio
async def test_practices_list_scope_upcoming(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """scope=upcoming returns only upcoming practices."""
    token = await _make_admin(client, db_session)
    master_id = await _make_master(client, db_session)
    await _create_practice(
        db_session, master_id, scheduled_at=datetime.now(UTC) + timedelta(days=3),
    )
    await db_session.commit()

    resp = await client.get(
        PRACTICES_URL, params={"scope": "upcoming", "limit": 100},
        headers=auth_headers(token),
    )
    assert resp.status_code == 200
    assert all(it["status"] == "upcoming" for it in resp.json()["items"])


@pytest.mark.asyncio
async def test_practices_list_scope_past(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """scope=past returns only past practices."""
    token = await _make_admin(client, db_session)
    master_id = await _make_master(client, db_session)
    await _create_practice(
        db_session, master_id,
        scheduled_at=datetime.now(UTC) - timedelta(days=3),
        status=PracticeStatus.COMPLETED.value,
    )
    await db_session.commit()

    resp = await client.get(
        PRACTICES_URL, params={"scope": "past", "limit": 100},
        headers=auth_headers(token),
    )
    assert resp.status_code == 200
    assert all(it["status"] == "past" for it in resp.json()["items"])


@pytest.mark.asyncio
async def test_practices_list_pagination(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """limit caps the page; total counts the full set."""
    token = await _make_admin(client, db_session)
    master_id = await _make_master(client, db_session)
    for i in range(3):
        await _create_practice(
            db_session, master_id,
            scheduled_at=datetime.now(UTC) + timedelta(days=i + 1),
        )
    await db_session.commit()

    resp = await client.get(
        PRACTICES_URL, params={"limit": 2, "offset": 0}, headers=auth_headers(token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) <= 2
    assert data["total"] >= len(data["items"])


# ===================================================================
# GET /admin/practices/{id} -- detail
# ===================================================================


@pytest.mark.asyncio
async def test_practice_detail_upcoming(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Upcoming detail: booked/capacity + roster of registered participants."""
    token = await _make_admin(client, db_session)
    master_id = await _make_master(client, db_session)
    practice = await _create_practice(
        db_session, master_id,
        scheduled_at=datetime.now(UTC) + timedelta(days=2),
        max_participants=10, direction="yoga",
    )
    await _book(client, db_session, practice, 94001)
    await _book(client, db_session, practice, 94002)
    await db_session.commit()

    resp = await client.get(
        DETAIL_URL.format(practice_id=practice.id), headers=auth_headers(token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "upcoming"
    assert data["booked"] == 2
    assert data["attended"] == 0
    assert data["capacity"] == 10
    assert data["direction"] == "yoga"
    assert data["master_name"] == "Master"
    assert data["master_verified"] is True
    assert len(data["roster"]) == 2
    assert {"user_id", "name", "avatar_url", "status"} == set(data["roster"][0].keys())


@pytest.mark.asyncio
async def test_practice_detail_past_split_excludes_cancelled(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Past detail: attended/no_show roster; cancelled is excluded entirely."""
    token = await _make_admin(client, db_session)
    master_id = await _make_master(client, db_session)
    practice = await _create_practice(
        db_session, master_id,
        scheduled_at=datetime.now(UTC) - timedelta(days=2),
        status=PracticeStatus.COMPLETED.value,
    )
    await _book(client, db_session, practice, 94010, status=BookingStatus.ATTENDED.value)
    await _book(client, db_session, practice, 94011, status=BookingStatus.ATTENDED.value)
    await _book(client, db_session, practice, 94012, status=BookingStatus.NO_SHOW.value)
    await _book(client, db_session, practice, 94013, status=BookingStatus.CANCELLED.value)
    await db_session.commit()

    resp = await client.get(
        DETAIL_URL.format(practice_id=practice.id), headers=auth_headers(token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "past"
    # cancelled excluded from booked and roster.
    assert data["booked"] == 3
    assert data["attended"] == 2
    assert len(data["roster"]) == 3
    statuses = sorted(r["status"] for r in data["roster"])
    assert statuses == ["attended", "attended", "no_show"]


@pytest.mark.asyncio
async def test_practice_detail_404_missing(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Unknown practice id: 404."""
    token = await _make_admin(client, db_session)
    await db_session.commit()
    resp = await client.get(
        DETAIL_URL.format(practice_id=uuid4()), headers=auth_headers(token),
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_practice_detail_404_deleted(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Soft-deleted practice resolves to 404."""
    token = await _make_admin(client, db_session)
    master_id = await _make_master(client, db_session)
    practice = await _create_practice(
        db_session, master_id,
        scheduled_at=datetime.now(UTC) - timedelta(days=1),
        status=PracticeStatus.DELETED.value,
    )
    await db_session.commit()

    resp = await client.get(
        DETAIL_URL.format(practice_id=practice.id), headers=auth_headers(token),
    )
    assert resp.status_code == 404


# ===================================================================
# auth
# ===================================================================


@pytest.mark.asyncio
async def test_practices_no_auth(client: AsyncClient) -> None:
    resp = await client.get(PRACTICES_URL)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_practices_non_admin(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    auth = await login_user(client, telegram_id=94050, first_name="Plain")
    resp = await client.get(PRACTICES_URL, headers=auth_headers(auth["session_token"]))
    assert resp.status_code == 403
