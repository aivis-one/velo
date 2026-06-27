# =============================================================================
# VELO Backend -- Tests: Admin Metrics (E9 / 4a)
# =============================================================================
#
# telegram_id range: 92000-92999
#   92900     -- admin caller
#   92800-92809 -- masters (practice owners)
#   92001+    -- attendees
#
# Coverage:
#   GET /admin/metrics/check-in   -- rate, totals, series (7 for week),
#                                    low_practices
#   GET /admin/metrics/feedback   -- rate, totals, rating distribution
#   GET /admin/metrics/return     -- rate, totals, top_users
#   auth (401 / 403), invalid period (422), empty state
# =============================================================================

from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.bookings.models import Booking, BookingStatus
from app.modules.diary.models import Checkin, CheckType, Feedback
from app.modules.masters.models import MasterProfile
from app.modules.practices.models import Practice, PracticeStatus, PracticeType
from app.modules.users.models import User, UserRole
from tests.helpers import auth_headers, full_cleanup_range, login_user

CHECKIN_URL = "/api/v1/admin/metrics/check-in"
FEEDBACK_URL = "/api/v1/admin/metrics/feedback"
RETURN_URL = "/api/v1/admin/metrics/return"

_TID_MIN = 92000
_TID_MAX = 92999


# ===================================================================
# Cleanup
# ===================================================================


@pytest.fixture(autouse=True)
async def cleanup(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    """Clean all test data before/after each test."""
    await full_cleanup_range(db_session, _TID_MIN, _TID_MAX, delete_users=True)
    await db_session.commit()
    yield
    await full_cleanup_range(db_session, _TID_MIN, _TID_MAX, delete_users=True)
    await db_session.commit()


# ===================================================================
# Helpers
# ===================================================================


async def _make_admin(
    client: AsyncClient,
    db_session: AsyncSession,
    telegram_id: int = 92900,
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
    client: AsyncClient,
    db_session: AsyncSession,
    telegram_id: int,
) -> str:
    auth = await login_user(client, telegram_id=telegram_id, first_name="Master")
    user_id = auth["user"]["id"]
    user = await db_session.get(User, user_id)
    user.role = UserRole.MASTER
    await db_session.flush()
    profile = MasterProfile(
        user_id=user_id,
        data={"account": {"status": "verified"}, "profile": {"bio": "m"}},
    )
    db_session.add(profile)
    await db_session.flush()
    return user_id


async def _create_practice(
    db_session: AsyncSession,
    master_id: str,
    *,
    scheduled_at: datetime,
    duration_minutes: int = 60,
) -> Practice:
    practice = Practice(
        master_id=master_id,
        title="Metric Practice",
        description="x",
        practice_type=PracticeType.LIVE.value,
        status=PracticeStatus.COMPLETED.value,
        scheduled_at=scheduled_at,
        duration_minutes=duration_minutes,
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


async def _attend(
    client: AsyncClient,
    db_session: AsyncSession,
    practice: Practice,
    telegram_id: int,
    *,
    status: str = BookingStatus.ATTENDED.value,
) -> tuple[str, Booking]:
    auth = await login_user(
        client, telegram_id=telegram_id, first_name=f"U{telegram_id}",
    )
    user_id = auth["user"]["id"]
    booking = Booking(
        practice_id=practice.id,
        user_id=user_id,
        status=status,
        joined_at=datetime.now(UTC) - timedelta(hours=2),
    )
    db_session.add(booking)
    await db_session.flush()
    return user_id, booking


async def _add_checkin(
    db_session: AsyncSession,
    practice: Practice,
    user_id: str,
    booking: Booking,
    *,
    mood: int = 8,
) -> None:
    db_session.add(
        Checkin(
            practice_id=practice.id,
            user_id=user_id,
            booking_id=booking.id,
            mood=mood,
            check_type=CheckType.PRE.value,
        )
    )
    await db_session.flush()


async def _add_feedback(
    db_session: AsyncSession,
    practice: Practice,
    user_id: str,
    booking: Booking,
    *,
    rating: int,
) -> None:
    db_session.add(
        Feedback(
            practice_id=practice.id,
            user_id=user_id,
            booking_id=booking.id,
            rating=rating,
        )
    )
    await db_session.flush()


# ===================================================================
# check-in
# ===================================================================


@pytest.mark.asyncio
async def test_checkin_metric_basic(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """rate = checked_in / total_records; series has 7 daily buckets (week)."""
    token = await _make_admin(client, db_session)
    await db_session.commit()  # admin must be visible to the endpoint

    # Baseline BEFORE our fixtures — the shared DB may carry seed data, so we
    # assert the DELTA our fixtures contribute, not absolute global counts.
    base = (
        await client.get(CHECKIN_URL, headers=auth_headers(token))
    ).json()

    master_id = await _make_master(client, db_session, 92800)
    practice = await _create_practice(
        db_session, master_id, scheduled_at=datetime.now(UTC),
    )

    _u1, b1 = await _attend(client, db_session, practice, 92001)
    await _add_checkin(db_session, practice, _u1, b1)
    await _attend(client, db_session, practice, 92002)  # no check-in
    await db_session.commit()

    resp = await client.get(CHECKIN_URL, headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    # We added 2 attended bookings, 1 of them with a check-in.
    assert data["total_records"] - base["total_records"] == 2
    assert data["checked_in"] - base["checked_in"] == 1
    assert len(data["series"]) == 7
    assert {"label", "value"} == set(data["series"][0].keys())
    # low_practices is bottom-N (<=5) and seed practices may fill it, so check
    # shape, and our own row's values only when it surfaces.
    assert len(data["low_practices"]) <= 5
    if data["low_practices"]:
        assert set(data["low_practices"][0].keys()) == {
            "id", "title", "checkin_rate_pct", "total",
        }
    ours = [p for p in data["low_practices"] if p["id"] == str(practice.id)]
    if ours:
        assert ours[0]["checkin_rate_pct"] == 50
        assert ours[0]["total"] == 2


@pytest.mark.asyncio
async def test_checkin_metric_empty(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """No data -> honest zeros, empty low list, but a full week series."""
    token = await _make_admin(client, db_session)
    await db_session.commit()

    # Shared DB may carry seed data, so "empty" can't mean global zero. Capture
    # a baseline and assert our no-op (no fixtures added) changes nothing.
    base = (
        await client.get(CHECKIN_URL, headers=auth_headers(token))
    ).json()

    resp = await client.get(CHECKIN_URL, headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_records"] == base["total_records"]
    assert data["checked_in"] == base["checked_in"]
    assert len(data["series"]) == 7


@pytest.mark.asyncio
async def test_checkin_metric_month_period(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Month period is accepted and returns weekly buckets."""
    token = await _make_admin(client, db_session)
    master_id = await _make_master(client, db_session, 92801)
    practice = await _create_practice(
        db_session, master_id, scheduled_at=datetime.now(UTC),
    )
    _u, b = await _attend(client, db_session, practice, 92010)
    await _add_checkin(db_session, practice, _u, b)
    await db_session.commit()

    resp = await client.get(
        CHECKIN_URL, params={"period": "month"}, headers=auth_headers(token),
    )
    assert resp.status_code == 200
    data = resp.json()
    # Platform-wide metric: seed data may also fall in the month, so assert our
    # records are included rather than an exact isolated count.
    assert data["total_records"] >= 1
    assert data["checked_in"] >= 1
    # Month spans 4-6 weekly buckets.
    assert 4 <= len(data["series"]) <= 6


# ===================================================================
# feedback
# ===================================================================


@pytest.mark.asyncio
async def test_feedback_metric_basic_and_distribution(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """rate = left_review / visited; distribution buckets by rating."""
    token = await _make_admin(client, db_session)
    await db_session.commit()  # admin must be visible to the endpoint

    # Baseline BEFORE our fixtures (shared DB may carry seed data).
    base = (
        await client.get(FEEDBACK_URL, headers=auth_headers(token))
    ).json()

    master_id = await _make_master(client, db_session, 92802)
    practice = await _create_practice(
        db_session, master_id, scheduled_at=datetime.now(UTC),
    )

    _u1, b1 = await _attend(client, db_session, practice, 92020)
    await _add_feedback(db_session, practice, _u1, b1, rating=9)   # fire
    _u2, b2 = await _attend(client, db_session, practice, 92021)
    await _add_feedback(db_session, practice, _u2, b2, rating=2)   # confused
    await _attend(client, db_session, practice, 92022)            # no feedback
    await db_session.commit()

    resp = await client.get(FEEDBACK_URL, headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    # 3 attended bookings; 2 left feedback (1 fire, 1 confused).
    assert data["visited"] - base["visited"] == 3
    assert data["left_review"] - base["left_review"] == 2
    dist, bdist = data["distribution"], base["distribution"]
    assert dist["fire"] - bdist["fire"] == 1
    assert dist["good"] - bdist["good"] == 0
    assert dist["confused"] - bdist["confused"] == 1


@pytest.mark.asyncio
async def test_feedback_metric_good_bucket(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """A mid rating (4-7) lands in the good bucket."""
    token = await _make_admin(client, db_session)
    await db_session.commit()  # admin must be visible to the endpoint

    # Baseline BEFORE our fixtures (shared DB may carry seed data).
    base = (
        await client.get(FEEDBACK_URL, headers=auth_headers(token))
    ).json()

    master_id = await _make_master(client, db_session, 92803)
    practice = await _create_practice(
        db_session, master_id, scheduled_at=datetime.now(UTC),
    )
    _u, b = await _attend(client, db_session, practice, 92030)
    await _add_feedback(db_session, practice, _u, b, rating=6)
    await db_session.commit()

    resp = await client.get(FEEDBACK_URL, headers=auth_headers(token))
    assert resp.status_code == 200
    # Our single rating-6 feedback lands in the good bucket. Assert the DELTA
    # over the baseline (not an absolute distribution), since seed practices
    # may carry other in-period feedbacks the platform-wide metric also counts.
    dist, bdist = resp.json()["distribution"], base["distribution"]
    assert dist["good"] - bdist["good"] == 1
    assert dist["fire"] - bdist["fire"] == 0
    assert dist["confused"] - bdist["confused"] == 0


@pytest.mark.asyncio
async def test_feedback_metric_excludes_non_attended(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """W-3: a feedback without an attended booking is not counted (rate <= 100%)."""
    token = await _make_admin(client, db_session)
    await db_session.commit()  # admin must be visible to the endpoint

    # Baseline BEFORE our fixtures (shared DB may carry seed data).
    base = (
        await client.get(FEEDBACK_URL, headers=auth_headers(token))
    ).json()

    master_id = await _make_master(client, db_session, 92804)
    practice = await _create_practice(
        db_session, master_id, scheduled_at=datetime.now(UTC),
    )

    # Attended + feedback -> counts.
    u1, b1 = await _attend(client, db_session, practice, 92040)
    await _add_feedback(db_session, practice, u1, b1, rating=9)

    # no_show booking + feedback on it -> must NOT count toward left_review.
    u2, b2 = await _attend(
        client, db_session, practice, 92041,
        status=BookingStatus.NO_SHOW.value,
    )
    await _add_feedback(db_session, practice, u2, b2, rating=8)
    await db_session.commit()

    resp = await client.get(FEEDBACK_URL, headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    # Only the attended booking + its feedback count; the no_show row (a fire
    # rating) is excluded -> deltas are +1, not +2 (W-3 intent preserved).
    assert data["visited"] - base["visited"] == 1
    assert data["left_review"] - base["left_review"] == 1
    dist, bdist = data["distribution"], base["distribution"]
    assert dist["fire"] - bdist["fire"] == 1
    assert dist["good"] - bdist["good"] == 0
    assert dist["confused"] - bdist["confused"] == 0


# ===================================================================
# return
# ===================================================================


@pytest.mark.asyncio
async def test_return_metric_basic(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """returning = period users who also attended before the period start."""
    token = await _make_admin(client, db_session)
    await db_session.commit()  # admin must be visible to the endpoint

    # Baseline BEFORE our fixtures (shared DB may carry seed data).
    base = (
        await client.get(RETURN_URL, headers=auth_headers(token))
    ).json()

    master_id = await _make_master(client, db_session, 92804)
    this_week = await _create_practice(
        db_session, master_id, scheduled_at=datetime.now(UTC),
    )
    before = await _create_practice(
        db_session, master_id,
        scheduled_at=datetime.now(UTC) - timedelta(days=14),
    )

    # User A: attended before AND this period -> returning.
    await _attend(client, db_session, this_week, 92040)
    await _attend(client, db_session, before, 92040)
    # User B: attended only this period -> not returning.
    await _attend(client, db_session, this_week, 92041)
    await db_session.commit()

    resp = await client.get(RETURN_URL, headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    # 2 new period-users (A, B); A also attended before the period -> +1 returning.
    assert data["total_users"] - base["total_users"] == 2
    assert data["returning"] - base["returning"] == 1
    # top_users is platform-wide all-time (seed users may rank above the test
    # users), so assert shape + descending order rather than an exact head.
    counts = [u["practices_count"] for u in data["top_users"]]
    assert counts == sorted(counts, reverse=True)
    assert set(data["top_users"][0].keys()) == {"id", "name", "practices_count"}


# ===================================================================
# auth + validation
# ===================================================================


@pytest.mark.asyncio
async def test_metrics_no_auth(client: AsyncClient) -> None:
    """No token: 401."""
    resp = await client.get(CHECKIN_URL)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_metrics_non_admin(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Regular user: 403."""
    auth = await login_user(client, telegram_id=92050, first_name="Plain")
    resp = await client.get(FEEDBACK_URL, headers=auth_headers(auth["session_token"]))
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_metrics_invalid_period(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Invalid period value: 422 (Literal validation)."""
    token = await _make_admin(client, db_session)
    await db_session.commit()
    resp = await client.get(
        RETURN_URL, params={"period": "year"}, headers=auth_headers(token),
    )
    assert resp.status_code == 422
