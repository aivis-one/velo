# =============================================================================
# VELO Backend -- Tests: Admin Stats Overview (E7, period-scoped dashboard)
# =============================================================================
#
# telegram_id ranges:
#   94900       -- admin caller
#   94800-94809 -- masters (practice owners)
#   94001-94199 -- regular users (participants / buyers / reporters)
#
# Platform-wide metrics: the shared test DB may carry seed data, so tests
# capture a baseline and assert the DELTA their fixtures contribute (mirrors
# test_admin_metrics) rather than absolute global counts.
#
# Coverage:
#   GET /admin/stats/overview
#     - auth: no auth (401), non-admin (403), invalid period (422)
#     - new_users / new_masters counts (period, by created_at)
#     - practices_count (period) + excludes draft/deleted/cancelled
#     - revenue_cents + commission_cents (period)
#     - engagement rates present, integer, 0..100; deltas int|null
#     - pending_reports (period-independent)
#     - month period accepted
# =============================================================================

from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.bookings.models import Booking, BookingStatus
from app.modules.diary.models import Checkin, CheckType, Feedback
from app.modules.masters.models import MasterProfile
from app.modules.payments.models import (
    CompanyLedger,
    CompanyLedgerType,
    Purchase,
    PurchaseStatus,
)
from app.modules.practices.models import Practice, PracticeStatus, PracticeType
from app.modules.reports.models import Report, ReportStatus
from app.modules.users.models import User, UserRole
from tests.helpers import auth_headers, login_user, full_cleanup_range

OVERVIEW_URL = "/api/v1/admin/stats/overview"

_TID_MIN = 94000
_TID_MAX = 94999


# ===================================================================
# Cleanup
# ===================================================================


@pytest.fixture(autouse=True)
async def cleanup(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    """Clean all test data before/after each test (ORM, no raw SQL)."""
    await _do_cleanup(db_session)
    yield
    await _do_cleanup(db_session)


async def _do_cleanup(session: AsyncSession) -> None:
    """Full ORM cleanup for telegram_id 94000-94999."""
    await full_cleanup_range(session, _TID_MIN, _TID_MAX, delete_users=False)
    await session.commit()


# ===================================================================
# Helpers
# ===================================================================


async def _make_admin(
    client: AsyncClient,
    db_session: AsyncSession,
    telegram_id: int = 94900,
) -> str:
    """Create an admin user, return session token."""
    auth = await login_user(
        client, telegram_id=telegram_id, first_name="OverviewAdmin",
    )
    await db_session.execute(
        update(User)
        .where(User.id == auth["user"]["id"])
        .values(role=UserRole.ADMIN.value)
    )
    await db_session.commit()
    return auth["session_token"]


async def _make_master(
    client: AsyncClient,
    db_session: AsyncSession,
    telegram_id: int,
) -> str:
    """Create a verified master, return master user_id (str)."""
    auth = await login_user(
        client, telegram_id=telegram_id, first_name="Master",
    )
    user_id = auth["user"]["id"]
    await db_session.execute(
        update(User)
        .where(User.id == user_id)
        .values(role=UserRole.MASTER.value)
    )
    profile = MasterProfile(
        user_id=UUID(user_id),
        data={"account": {"status": "verified"}},
    )
    db_session.add(profile)
    await db_session.commit()
    return user_id


async def _create_practice(
    db_session: AsyncSession,
    master_id: str,
    *,
    scheduled_at: datetime,
    status: str = PracticeStatus.COMPLETED.value,
) -> Practice:
    """Create a practice owned by the master with the given schedule/status."""
    practice = Practice(
        master_id=UUID(master_id),
        practice_type=PracticeType.LIVE.value,
        status=status,
        title="Overview Practice",
        scheduled_at=scheduled_at,
        duration_minutes=60,
        timezone="UTC",
    )
    db_session.add(practice)
    await db_session.flush()
    await db_session.commit()
    return practice


async def _attend(
    client: AsyncClient,
    db_session: AsyncSession,
    practice: Practice,
    telegram_id: int,
) -> tuple[str, Booking]:
    """Log in a participant and add an ATTENDED booking. Returns (user_id, booking)."""
    auth = await login_user(
        client, telegram_id=telegram_id, first_name="Part",
    )
    user_id = auth["user"]["id"]
    booking = Booking(
        practice_id=practice.id,
        user_id=UUID(user_id),
        status=BookingStatus.ATTENDED.value,
    )
    db_session.add(booking)
    await db_session.flush()
    await db_session.commit()
    return user_id, booking


async def _add_checkin(
    db_session: AsyncSession,
    practice: Practice,
    user_id: str,
    booking: Booking,
    *,
    mood: int = 8,
) -> None:
    """Add a PRE check-in for the participant's booking."""
    db_session.add(
        Checkin(
            practice_id=practice.id,
            user_id=UUID(user_id),
            booking_id=booking.id,
            mood=mood,
            check_type=CheckType.PRE.value,
        )
    )
    await db_session.commit()


async def _add_feedback(
    db_session: AsyncSession,
    practice: Practice,
    user_id: str,
    booking: Booking,
    *,
    rating: int = 9,
) -> None:
    """Add a feedback for the participant's booking."""
    db_session.add(
        Feedback(
            practice_id=practice.id,
            user_id=UUID(user_id),
            booking_id=booking.id,
            rating=rating,
        )
    )
    await db_session.commit()


async def _complete_purchase(
    client: AsyncClient,
    db_session: AsyncSession,
    practice: Practice,
    telegram_id: int,
    *,
    paid_cents: int = 10000,
    commission_cents: int = 1500,
) -> Purchase:
    """Create a buyer + a completed Purchase (completed now) on the practice."""
    auth = await login_user(
        client, telegram_id=telegram_id, first_name="Buyer",
    )
    user_id = auth["user"]["id"]
    booking = Booking(
        practice_id=practice.id,
        user_id=UUID(user_id),
        status=BookingStatus.ATTENDED.value,
    )
    db_session.add(booking)
    await db_session.flush()

    purchase = Purchase(
        user_id=UUID(user_id),
        practice_id=practice.id,
        booking_id=booking.id,
        amount_cents=paid_cents,
        discount_cents=0,
        paid_cents=paid_cents,
        currency="eur",
        commission_cents=commission_cents,
        status=PurchaseStatus.COMPLETED.value,
        completed_at=datetime.now(UTC),
    )
    db_session.add(purchase)
    await db_session.commit()
    return purchase


async def _add_commission(
    db_session: AsyncSession,
    purchase: Purchase,
    *,
    amount_cents: int = 1500,
) -> None:
    """Book a COMMISSION company-ledger entry (created now) for the purchase."""
    db_session.add(
        CompanyLedger(
            amount_cents=amount_cents,
            type=CompanyLedgerType.COMMISSION.value,
            reason="commission:test",
            reference_id=purchase.id,
        )
    )
    await db_session.commit()


async def _add_report(
    db_session: AsyncSession,
    reporter_id: str,
    target_id: str,
) -> None:
    """Create a pending report by reporter against the target user."""
    db_session.add(
        Report(
            reporter_id=UUID(reporter_id),
            target_type="user",
            target_id=UUID(target_id),
            reason="overview test report",
            status=ReportStatus.PENDING.value,
        )
    )
    await db_session.commit()


# ===================================================================
# Auth
# ===================================================================


async def test_overview_no_auth(client: AsyncClient) -> None:
    """No Authorization header -> 401."""
    resp = await client.get(OVERVIEW_URL)
    assert resp.status_code == 401


async def test_overview_requires_admin(
    client: AsyncClient,
) -> None:
    """A non-admin user -> 403."""
    data = await login_user(
        client, telegram_id=94001, first_name="Plain",
    )
    resp = await client.get(
        OVERVIEW_URL, headers=auth_headers(data["session_token"]),
    )
    assert resp.status_code == 403


async def test_overview_invalid_period(
    client: AsyncClient, db_session: AsyncSession,
) -> None:
    """Invalid period value -> 422 (Literal validation, P-11)."""
    token = await _make_admin(client, db_session)
    resp = await client.get(
        f"{OVERVIEW_URL}?period=year", headers=auth_headers(token),
    )
    assert resp.status_code == 422


# ===================================================================
# Growth counts
# ===================================================================


async def test_new_users_counts(
    client: AsyncClient, db_session: AsyncSession,
) -> None:
    """new_users increases by the number of users registered in the period."""
    token = await _make_admin(client, db_session)
    base = (
        await client.get(OVERVIEW_URL, headers=auth_headers(token))
    ).json()

    await login_user(client, telegram_id=94010, first_name="U1")
    await login_user(client, telegram_id=94011, first_name="U2")

    resp = await client.get(OVERVIEW_URL, headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()["new_users"] - base["new_users"] == 2


async def test_new_masters_counts(
    client: AsyncClient, db_session: AsyncSession,
) -> None:
    """new_masters increases for a newly-registered master account."""
    token = await _make_admin(client, db_session)
    base = (
        await client.get(OVERVIEW_URL, headers=auth_headers(token))
    ).json()

    await _make_master(client, db_session, 94800)

    resp = await client.get(OVERVIEW_URL, headers=auth_headers(token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["new_masters"] - base["new_masters"] == 1
    # The master is also a freshly-registered user.
    assert body["new_users"] - base["new_users"] == 1


async def test_practices_count_excludes_hidden(
    client: AsyncClient, db_session: AsyncSession,
) -> None:
    """practices_count counts period practices, excluding draft/deleted/cancelled."""
    token = await _make_admin(client, db_session)
    master_id = await _make_master(client, db_session, 94801)
    now = datetime.now(UTC)

    base = (
        await client.get(OVERVIEW_URL, headers=auth_headers(token))
    ).json()

    await _create_practice(db_session, master_id, scheduled_at=now)
    await _create_practice(db_session, master_id, scheduled_at=now)
    for status in (
        PracticeStatus.DRAFT.value,
        PracticeStatus.DELETED.value,
        PracticeStatus.CANCELLED.value,
    ):
        await _create_practice(
            db_session, master_id, scheduled_at=now, status=status,
        )

    resp = await client.get(OVERVIEW_URL, headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()["practices_count"] - base["practices_count"] == 2


# ===================================================================
# Revenue
# ===================================================================


async def test_revenue_and_commission(
    client: AsyncClient, db_session: AsyncSession,
) -> None:
    """revenue_cents and commission_cents reflect period purchases/commission."""
    token = await _make_admin(client, db_session)
    master_id = await _make_master(client, db_session, 94802)
    now = datetime.now(UTC)
    practice = await _create_practice(db_session, master_id, scheduled_at=now)

    base = (
        await client.get(OVERVIEW_URL, headers=auth_headers(token))
    ).json()

    purchase = await _complete_purchase(
        client, db_session, practice, 94020,
        paid_cents=10000, commission_cents=1500,
    )
    await _add_commission(db_session, purchase, amount_cents=1500)

    resp = await client.get(OVERVIEW_URL, headers=auth_headers(token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["revenue_cents"] - base["revenue_cents"] == 10000
    assert body["commission_cents"] - base["commission_cents"] == 1500


# ===================================================================
# Engagement rates (shape -- formula correctness covered by metrics tests)
# ===================================================================


async def test_rates_shape(
    client: AsyncClient, db_session: AsyncSession,
) -> None:
    """Rate fields are integers in 0..100; deltas are int or null."""
    token = await _make_admin(client, db_session)
    master_id = await _make_master(client, db_session, 94803)
    now = datetime.now(UTC)
    practice = await _create_practice(db_session, master_id, scheduled_at=now)

    user_id, booking = await _attend(client, db_session, practice, 94030)
    await _add_checkin(db_session, practice, user_id, booking)
    await _add_feedback(db_session, practice, user_id, booking, rating=9)

    resp = await client.get(OVERVIEW_URL, headers=auth_headers(token))
    assert resp.status_code == 200
    body = resp.json()
    for key in ("checkin_rate_pct", "feedback_rate_pct", "return_rate_pct"):
        assert isinstance(body[key], int)
        assert 0 <= body[key] <= 100
    for key in ("checkin_rate_delta", "feedback_rate_delta", "return_rate_delta"):
        assert body[key] is None or isinstance(body[key], int)


# ===================================================================
# Pending reports (period-independent)
# ===================================================================


async def test_pending_reports_counts(
    client: AsyncClient, db_session: AsyncSession,
) -> None:
    """pending_reports increases by the number of pending reports created."""
    token = await _make_admin(client, db_session)
    reporter = await login_user(
        client, telegram_id=94040, first_name="Reporter",
    )
    target = await login_user(
        client, telegram_id=94041, first_name="Target",
    )

    base = (
        await client.get(OVERVIEW_URL, headers=auth_headers(token))
    ).json()

    await _add_report(db_session, reporter["user"]["id"], target["user"]["id"])

    resp = await client.get(OVERVIEW_URL, headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()["pending_reports"] - base["pending_reports"] == 1


# ===================================================================
# Month period
# ===================================================================


async def test_month_period(
    client: AsyncClient, db_session: AsyncSession,
) -> None:
    """Month period is accepted and returns the full payload."""
    token = await _make_admin(client, db_session)
    resp = await client.get(
        f"{OVERVIEW_URL}?period=month", headers=auth_headers(token),
    )
    assert resp.status_code == 200
    body = resp.json()
    for key in (
        "new_users", "new_masters", "practices_count",
        "revenue_cents", "commission_cents",
        "checkin_rate_pct", "feedback_rate_pct", "return_rate_pct",
        "pending_reports",
    ):
        assert key in body
