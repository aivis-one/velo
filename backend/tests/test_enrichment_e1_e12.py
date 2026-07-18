# =============================================================================
# VELO Backend -- Tests: Card Enrichment (E1 remainder + E12 attendance)
# =============================================================================
#
# telegram_id range: 98000-98999
#
# Additive, read-only response enrichments:
#   E1 remainder -- reviewer user_id on the master-wide reviews feed
#     (GET /masters/me/reviews). The per-practice feed's user_id is covered
#     in test_reviews.py.
#   E12 + aggregate -- checkin_count / attended / no_show on the practice card:
#     * master's own list (GET /masters/me/practices) -- always shown
#     * owner's detail   (GET /practices/{id})        -- shown to the owner
#     * non-owner detail (GET /practices/{id})        -- None (no_show sensitive)
#     * public feed      (GET /practices)             -- None (never computed)
#
# checkin_count counts DISTINCT users with a PRE check-in; POST check-ins are a
# future socket and are excluded. attended / no_show are booking-status counts.
#
# Counts are exercised with direct ORM writes (bookings + check-ins) -- we do
# not drive the full booking -> attend -> feedback flow here; the aggregate
# queries only care about the rows existing.
# =============================================================================

from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.bookings.models import Booking, BookingStatus
from app.modules.diary.models import Checkin, CheckType, Feedback
from app.modules.masters.models import MasterProfile
from app.modules.practices.models import Practice, PracticeStatus, PracticeType
from app.modules.users.models import User, UserRole
from tests.helpers import auth_headers, login_user

MASTER_PRACTICES_URL = "/api/v1/masters/me/practices"
MASTER_REVIEWS_URL = "/api/v1/masters/me/reviews"
PRACTICE_DETAIL_URL = "/api/v1/practices/{practice_id}"
PUBLIC_FEED_URL = "/api/v1/practices"

# telegram_id range for this test file.
_TID_MIN = 98000
_TID_MAX = 98999


# ===================================================================
# Cleanup
# ===================================================================


async def _do_cleanup(session: AsyncSession) -> None:
    """Delete all test entities for telegram_id 98000-98999 (FK-safe order)."""
    await session.rollback()

    user_ids_subq = (
        select(User.id).where(
            User.telegram_id.between(_TID_MIN, _TID_MAX),
        )
    )

    # 1. feedbacks (FK -> bookings, practices, users).
    await session.execute(
        Feedback.__table__.delete().where(
            Feedback.user_id.in_(user_ids_subq),
        )
    )
    # 2. checkins (FK -> bookings, practices, users).
    await session.execute(
        Checkin.__table__.delete().where(
            Checkin.user_id.in_(user_ids_subq),
        )
    )
    # 3. audit_logs for our users.
    from app.core.audit import AuditLog
    await session.execute(
        AuditLog.__table__.delete().where(
            AuditLog.actor_id.in_(user_ids_subq),
        )
    )
    # 4. bookings (FK -> practices, users).
    await session.execute(
        Booking.__table__.delete().where(
            Booking.user_id.in_(user_ids_subq),
        )
    )
    # 5. practices (FK -> master_profiles).
    await session.execute(
        Practice.__table__.delete().where(
            Practice.master_id.in_(user_ids_subq),
        )
    )
    # 6. master_profiles (FK -> users).
    await session.execute(
        MasterProfile.__table__.delete().where(
            MasterProfile.user_id.in_(user_ids_subq),
        )
    )
    # 7. users.
    await session.execute(
        User.__table__.delete().where(
            User.telegram_id.between(_TID_MIN, _TID_MAX),
        )
    )
    await session.commit()


@pytest.fixture(autouse=True)
async def cleanup(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    """Clean test data before/after each test in FK-safe order."""
    await _do_cleanup(db_session)
    yield
    await _do_cleanup(db_session)


# ===================================================================
# Helpers
# ===================================================================


async def _make_verified_master(
    client: AsyncClient,
    db_session: AsyncSession,
    telegram_id: int,
) -> dict:
    """Create a verified master and return the auth dict."""
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
    status: str,
    title: str = "Enrichment Practice",
    scheduled_at: datetime | None = None,
) -> Practice:
    """Create a practice in the given status.

    Defaults scheduled_at to the past for completed practices and to the
    future for scheduled ones (so a scheduled practice shows in the default
    public feed, which is future-only).
    """
    if scheduled_at is None:
        if status == PracticeStatus.SCHEDULED.value:
            scheduled_at = datetime.now(UTC) + timedelta(days=3)
        else:
            scheduled_at = datetime.now(UTC) - timedelta(hours=3)

    practice = Practice(
        master_id=master_id,
        title=title,
        description="For enrichment testing",
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


async def _add_participant(
    db_session: AsyncSession,
    client: AsyncClient,
    practice: Practice,
    telegram_id: int,
    *,
    booking_status: str,
    checkin_type: str | None = None,
) -> dict:
    """Register a user with a booking (given status) and an optional check-in.

    checkin_type is a CheckType value ("pre" / "post") or None for no check-in.
    Direct ORM writes -- bypasses the API time-window checks.
    """
    auth = await login_user(
        client, telegram_id=telegram_id, first_name=f"User{telegram_id}",
    )
    user_id = auth["user"]["id"]

    booking = Booking(
        practice_id=practice.id,
        user_id=user_id,
        status=booking_status,
        joined_at=datetime.now(UTC) - timedelta(hours=2),
    )
    db_session.add(booking)
    await db_session.flush()

    if checkin_type is not None:
        checkin = Checkin(
            practice_id=practice.id,
            user_id=user_id,
            booking_id=booking.id,
            mood=7,
            check_type=checkin_type,
        )
        db_session.add(checkin)
        await db_session.flush()

    return auth


async def _add_review(
    db_session: AsyncSession,
    client: AsyncClient,
    practice: Practice,
    telegram_id: int,
    *,
    rating: int,
    comment: str | None = None,
    first_name: str | None = None,
) -> dict:
    """Register an attended participant who left a feedback (a "review")."""
    auth = await login_user(
        client,
        telegram_id=telegram_id,
        first_name=first_name or f"User{telegram_id}",
    )
    user_id = auth["user"]["id"]

    booking = Booking(
        practice_id=practice.id,
        user_id=user_id,
        status=BookingStatus.ATTENDED.value,
        joined_at=datetime.now(UTC) - timedelta(hours=2),
    )
    db_session.add(booking)
    await db_session.flush()

    feedback = Feedback(
        practice_id=practice.id,
        user_id=user_id,
        booking_id=booking.id,
        rating=rating,
        comment=comment,
    )
    db_session.add(feedback)
    await db_session.flush()

    return auth


def _find(items: list[dict], practice_id: object) -> dict:
    """Return the response item for a given practice id (string-compared)."""
    target = str(practice_id)
    for item in items:
        if item["id"] == target:
            return item
    raise AssertionError(f"practice {target} not in response items")


# ===================================================================
# E12: master's own list exposes the counts (PRE-only check-ins)
# ===================================================================


@pytest.mark.asyncio
async def test_master_list_exposes_attendance_counts(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """GET /masters/me/practices carries checkin_count / attended / no_show.

    Setup: 3 attended bookings (two with a PRE check-in, one with a POST
    check-in) and 1 no_show. Expect attended=3, no_show=1, and checkin_count=2
    (the POST check-in is excluded).
    """
    master = await _make_verified_master(client, db_session, telegram_id=98100)
    practice = await _create_practice(
        db_session, master["user"]["id"],
        status=PracticeStatus.COMPLETED.value,
    )

    await _add_participant(
        db_session, client, practice, 98101,
        booking_status=BookingStatus.ATTENDED.value,
        checkin_type=CheckType.PRE.value,
    )
    await _add_participant(
        db_session, client, practice, 98102,
        booking_status=BookingStatus.ATTENDED.value,
        checkin_type=CheckType.PRE.value,
    )
    await _add_participant(
        db_session, client, practice, 98103,
        booking_status=BookingStatus.ATTENDED.value,
        checkin_type=CheckType.POST.value,  # excluded from checkin_count
    )
    await _add_participant(
        db_session, client, practice, 98104,
        booking_status=BookingStatus.NO_SHOW.value,
    )
    await db_session.commit()

    resp = await client.get(
        MASTER_PRACTICES_URL,
        headers=auth_headers(master["session_token"]),
    )

    assert resp.status_code == 200
    item = _find(resp.json()["items"], practice.id)
    assert item["attended"] == 3
    assert item["no_show"] == 1
    assert item["checkin_count"] == 2


# ===================================================================
# E12: the owner's detail exposes the counts
# ===================================================================


@pytest.mark.asyncio
async def test_owner_detail_exposes_attendance_counts(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """GET /practices/{id} carries the counts for the owner master."""
    master = await _make_verified_master(client, db_session, telegram_id=98200)
    practice = await _create_practice(
        db_session, master["user"]["id"],
        status=PracticeStatus.COMPLETED.value,
    )

    await _add_participant(
        db_session, client, practice, 98201,
        booking_status=BookingStatus.ATTENDED.value,
        checkin_type=CheckType.PRE.value,
    )
    await _add_participant(
        db_session, client, practice, 98202,
        booking_status=BookingStatus.ATTENDED.value,
        checkin_type=CheckType.PRE.value,
    )
    await _add_participant(
        db_session, client, practice, 98203,
        booking_status=BookingStatus.NO_SHOW.value,
    )
    await db_session.commit()

    resp = await client.get(
        PRACTICE_DETAIL_URL.format(practice_id=practice.id),
        headers=auth_headers(master["session_token"]),
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["attended"] == 2
    assert body["no_show"] == 1
    assert body["checkin_count"] == 2


# ===================================================================
# E12 (variant B): a non-owner's detail hides the counts
# ===================================================================


@pytest.mark.asyncio
async def test_non_owner_detail_hides_attendance_counts(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """A non-owner viewing the detail gets None for all three counts.

    no_show is sensitive, so it is never exposed to a non-owner -- the whole
    trio is gated to the practice owner (variant B).
    """
    master = await _make_verified_master(client, db_session, telegram_id=98300)
    practice = await _create_practice(
        db_session, master["user"]["id"],
        status=PracticeStatus.COMPLETED.value,
    )
    # Data exists, but the non-owner must still see None.
    await _add_participant(
        db_session, client, practice, 98301,
        booking_status=BookingStatus.ATTENDED.value,
        checkin_type=CheckType.PRE.value,
    )
    await db_session.commit()

    viewer = await login_user(client, telegram_id=98310, first_name="Viewer")
    resp = await client.get(
        PRACTICE_DETAIL_URL.format(practice_id=practice.id),
        headers=auth_headers(viewer["session_token"]),
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["checkin_count"] is None
    assert body["attended"] is None
    assert body["no_show"] is None


# ===================================================================
# E12: the public feed never computes the counts
# ===================================================================


@pytest.mark.asyncio
async def test_public_feed_leaves_attendance_counts_none(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """GET /practices leaves all three counts None even when data exists."""
    master = await _make_verified_master(client, db_session, telegram_id=98400)
    # A scheduled future practice shows in the default (future-only) feed.
    practice = await _create_practice(
        db_session, master["user"]["id"],
        status=PracticeStatus.SCHEDULED.value,
    )
    # A booked user who checked in early -- data the feed must NOT surface.
    await _add_participant(
        db_session, client, practice, 98401,
        booking_status=BookingStatus.CONFIRMED.value,
        checkin_type=CheckType.PRE.value,
    )
    await db_session.commit()

    viewer = await login_user(client, telegram_id=98410, first_name="Viewer")
    resp = await client.get(
        f"{PUBLIC_FEED_URL}?master_id={master['user']['id']}",
        headers=auth_headers(viewer["session_token"]),
    )

    assert resp.status_code == 200
    item = _find(resp.json()["items"], practice.id)
    assert item["checkin_count"] is None
    assert item["attended"] is None
    assert item["no_show"] is None


# ===================================================================
# E1 remainder: master-wide reviews feed carries the reviewer user_id
# ===================================================================


@pytest.mark.asyncio
async def test_master_review_items_carry_user_id(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """GET /masters/me/reviews items expose user_id matching the author."""
    master = await _make_verified_master(client, db_session, telegram_id=98500)
    practice = await _create_practice(
        db_session, master["user"]["id"],
        status=PracticeStatus.COMPLETED.value,
    )
    reviewer = await _add_review(
        db_session, client, practice, 98501,
        rating=2, comment="Needs work.", first_name="Dana",
    )
    await db_session.commit()

    resp = await client.get(
        MASTER_REVIEWS_URL,
        headers=auth_headers(master["session_token"]),
    )

    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) == 1
    assert items[0]["user_id"] == reviewer["user"]["id"]
    assert items[0]["reviewer_name"] == "Dana"
    assert items[0]["practice_title"] == practice.title


# ===================================================================
# E12: counts resolve in exactly two queries regardless of page size
# ===================================================================


@pytest.mark.asyncio
async def test_attendance_counts_no_n_plus_one(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Resolving counts for several practices stays at two SELECTs.

    Mirrors test_series_card.py::test_series_meta_no_n_plus_one.
    """
    master = await _make_verified_master(client, db_session, telegram_id=98600)
    for i in range(3):
        practice = await _create_practice(
            db_session, master["user"]["id"],
            status=PracticeStatus.COMPLETED.value,
            title=f"P{i}",
        )
        await _add_participant(
            db_session, client, practice, 98610 + i * 10,
            booking_status=BookingStatus.ATTENDED.value,
            checkin_type=CheckType.PRE.value,
        )
        await _add_participant(
            db_session, client, practice, 98611 + i * 10,
            booking_status=BookingStatus.NO_SHOW.value,
        )
    await db_session.commit()

    from sqlalchemy import event
    from sqlalchemy.engine import Engine

    from app.core.database import get_session_factory
    from app.modules.practices.enrichment_service import _attendance_counts_for_practices

    factory = get_session_factory()
    async with factory() as s:
        practices = list(
            (
                await s.execute(
                    select(Practice).where(
                        Practice.master_id == UUID(master["user"]["id"])
                    )
                )
            ).scalars().all()
        )
        assert len(practices) == 3

        selects: list[str] = []

        def _count(conn, cursor, statement, *args, **kwargs) -> None:
            if statement.lstrip().upper().startswith("SELECT"):
                selects.append(statement)

        event.listen(Engine, "before_cursor_execute", _count)
        try:
            counts = await _attendance_counts_for_practices(practices, s)
        finally:
            event.remove(Engine, "before_cursor_execute", _count)

    # Two queries (checkins + bookings) for 3 practices -- no N+1.
    assert len(selects) == 2, selects
    assert len(counts) == 3
    # Each practice: 1 PRE check-in, 1 attended, 1 no_show.
    for practice in practices:
        assert counts[practice.id] == (1, 1, 1)
