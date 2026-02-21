# =============================================================================
# Test: Admin -- Data Consistency Semaphores (Phase 6.8)
# =============================================================================
#
# telegram_id ranges:
#   82001-82099 -- regular users
#   82100-82199 -- master users
#   82900-82999 -- admin users
# =============================================================================

from collections.abc import AsyncGenerator
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import text, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.bookings.models import Booking, BookingStatus
from app.modules.masters.models import MasterProfile
from app.modules.payments.models import (
    CompanyLedger,
    CompanyLedgerType,
    LedgerStatus,
    MasterLedger,
    Purchase,
    PurchaseStatus,
    UserLedger,
)
from app.modules.practices.models import Practice, PracticeStatus
from app.modules.users.models import User, UserRole
from tests.helpers import auth_headers, login_user

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CONSISTENCY_URL = "/api/v1/admin/consistency"

_CLEANUP_SQL_ORDER = [
    "DELETE FROM purchases WHERE user_id IN (SELECT id FROM users WHERE telegram_id BETWEEN 82000 AND 82999)",
    "DELETE FROM bookings WHERE user_id IN (SELECT id FROM users WHERE telegram_id BETWEEN 82000 AND 82999)",
    "DELETE FROM user_ledger WHERE user_id IN (SELECT id FROM users WHERE telegram_id BETWEEN 82000 AND 82999)",
    "DELETE FROM master_ledger WHERE user_id IN (SELECT id FROM users WHERE telegram_id BETWEEN 82000 AND 82999)",
    "DELETE FROM company_ledger WHERE reason LIKE '%phase68%'",
    "DELETE FROM audit_logs WHERE actor_id IN (SELECT id FROM users WHERE telegram_id BETWEEN 82000 AND 82999)",
    "DELETE FROM practices WHERE master_id IN (SELECT user_id FROM master_profiles WHERE user_id IN (SELECT id FROM users WHERE telegram_id BETWEEN 82000 AND 82999))",
    "DELETE FROM master_profiles WHERE user_id IN (SELECT id FROM users WHERE telegram_id BETWEEN 82000 AND 82999)",
    "UPDATE users SET role = 'user' WHERE telegram_id BETWEEN 82000 AND 82999",
]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
async def cleanup(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    """Clean test data before/after each test."""
    for sql in _CLEANUP_SQL_ORDER:
        await db_session.execute(text(sql))
    await db_session.commit()
    yield
    for sql in _CLEANUP_SQL_ORDER:
        await db_session.execute(text(sql))
    await db_session.commit()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
async def _make_admin(
    client: AsyncClient,
    db_session: AsyncSession,
    telegram_id: int = 82900,
) -> str:
    """Create admin user, return token."""
    auth = await login_user(
        client, telegram_id=telegram_id, first_name="ConsAdmin",
    )
    await db_session.execute(
        update(User)
        .where(User.id == auth["user"]["id"])
        .values(role=UserRole.ADMIN.value)
    )
    await db_session.commit()
    return auth["session_token"]


# ---------------------------------------------------------------------------
# Auth checks
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_consistency_no_auth(client: AsyncClient) -> None:
    """No Authorization header: 401."""
    resp = await client.get(CONSISTENCY_URL)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_consistency_non_admin(client: AsyncClient) -> None:
    """Regular user (not admin): 403."""
    auth = await login_user(client, telegram_id=82001, first_name="NotAdmin")
    resp = await client.get(
        CONSISTENCY_URL, headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Clean state -- all semaphores OK
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_consistency_clean_state(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """On a clean DB (no bookings/purchases), all semaphores pass."""
    token = await _make_admin(client, db_session)

    resp = await client.get(
        CONSISTENCY_URL, headers=auth_headers(token),
    )
    assert resp.status_code == 200
    data = resp.json()

    assert "items" in data
    assert "total" in data
    assert "ok_count" in data
    assert "alert_count" in data
    assert "run_at" in data

    # All 21 semaphores should be present.
    assert data["total"] == 21
    # On clean state, everything should be OK.
    assert data["alert_count"] == 0
    assert data["ok_count"] == 21

    # Verify all items have required fields.
    for item in data["items"]:
        assert "name" in item
        assert "category" in item
        assert "status" in item
        assert item["status"] == "OK"
        assert "expected" in item
        assert "actual" in item
        assert "criticality" in item


# ---------------------------------------------------------------------------
# Semaphore names coverage
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_consistency_all_semaphore_names(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """All 21 expected semaphores are present in response."""
    token = await _make_admin(client, db_session)

    resp = await client.get(
        CONSISTENCY_URL, headers=auth_headers(token),
    )
    data = resp.json()
    names = {item["name"] for item in data["items"]}

    expected_names = {
        "1.1_active_bookings_eq_active_purchases",
        "1.2_cancelled_bookings_eq_cancelled_purchases",
        "1.3_master_users_eq_verified_profiles",
        "1.4_bookings_all_have_purchase",
        "2.1_global_double_entry_sum_zero",
        "2.2_purchase_paid_eq_user_debits",
        "3.1_user_balance_eq_ledger_sum",
        "3.2_master_frozen_eq_ledger_sum",
        "3.3_master_available_eq_ledger_sum",
        "3.4_practice_participants_eq_booking_count",
        "3.5_promo_used_count_eq_purchase_count",
        "4.1_bookings_orphan_practice",
        "4.2_bookings_orphan_user",
        "4.3_purchases_orphan_user",
        "4.4_master_ledger_orphan_user",
        "5.1_no_frozen_for_completed_practices",
        "5.2_no_negative_master_available",
        "5.3_no_negative_user_balance",
        "5.4_attended_must_have_joined_at",
        "5.5_no_over_max_participants",
        "5.6_completed_purchases_have_audit",
    }
    assert names == expected_names


# ---------------------------------------------------------------------------
# 3.1 ALERT: User balance_cents mismatch
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_consistency_alert_user_balance_mismatch(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Direct balance_cents modification triggers 3.1 ALERT."""
    token = await _make_admin(client, db_session)

    # Create a user and add a ledger entry via ORM.
    user_auth = await login_user(
        client, telegram_id=82010, first_name="MismatchUser",
    )
    user_id = user_auth["user"]["id"]

    # Add a ledger entry (+1000 cents).
    entry = UserLedger(
        user_id=UUID(user_id),
        amount_cents=1000,
        status=LedgerStatus.DONE.value,
        reason="payment:phase68_test",
    )
    db_session.add(entry)
    await db_session.flush()

    # Manually set wrong cached balance (should be 1000, set to 500).
    await db_session.execute(
        update(User)
        .where(User.id == user_id)
        .values(balance_cents=500)
    )
    await db_session.commit()

    resp = await client.get(
        CONSISTENCY_URL, headers=auth_headers(token),
    )
    data = resp.json()

    # Find semaphore 3.1.
    sem_3_1 = next(
        item for item in data["items"]
        if item["name"] == "3.1_user_balance_eq_ledger_sum"
    )
    assert sem_3_1["status"] == "ALERT"
    assert data["alert_count"] >= 1


# ---------------------------------------------------------------------------
# 3.4 ALERT: current_participants mismatch
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_consistency_alert_participants_mismatch(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Stale current_participants triggers 3.4 ALERT."""
    token = await _make_admin(client, db_session)

    # Create a master.
    master_auth = await login_user(
        client, telegram_id=82100, first_name="ConsMaster",
    )
    master_user_id = UUID(master_auth["user"]["id"])
    await db_session.execute(
        update(User)
        .where(User.id == master_user_id)
        .values(role=UserRole.MASTER.value)
    )
    profile = MasterProfile(
        user_id=master_user_id,
        data={"account": {"status": "verified"}},
    )
    db_session.add(profile)
    await db_session.flush()

    # Create a practice with current_participants=5 but no bookings.
    practice = Practice(
        master_id=master_user_id,
        practice_type="live",
        status=PracticeStatus.SCHEDULED.value,
        title="Consistency Test Practice",
        scheduled_at=datetime.now(timezone.utc) + timedelta(days=1),
        duration_minutes=60,
        timezone="UTC",
        current_participants=5,  # Stale value -- no bookings exist.
        is_free=True,
        price_cents=0,
        currency="EUR",
    )
    db_session.add(practice)
    await db_session.commit()

    resp = await client.get(
        CONSISTENCY_URL, headers=auth_headers(token),
    )
    data = resp.json()

    # Find semaphore 3.4.
    sem_3_4 = next(
        item for item in data["items"]
        if item["name"] == "3.4_practice_participants_eq_booking_count"
    )
    assert sem_3_4["status"] == "ALERT"
    assert sem_3_4["details"]["stale_nonzero_without_bookings"] >= 1


# ---------------------------------------------------------------------------
# 5.3 ALERT: Negative user balance
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_consistency_alert_negative_balance(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """User with negative balance_cents triggers 5.3 ALERT."""
    token = await _make_admin(client, db_session)

    user_auth = await login_user(
        client, telegram_id=82020, first_name="NegUser",
    )
    user_id = user_auth["user"]["id"]

    # Force negative balance.
    await db_session.execute(
        update(User)
        .where(User.id == user_id)
        .values(balance_cents=-100)
    )
    await db_session.commit()

    resp = await client.get(
        CONSISTENCY_URL, headers=auth_headers(token),
    )
    data = resp.json()

    sem_5_3 = next(
        item for item in data["items"]
        if item["name"] == "5.3_no_negative_user_balance"
    )
    assert sem_5_3["status"] == "ALERT"
    assert int(sem_5_3["actual"]) >= 1
