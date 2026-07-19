# =============================================================================
# VELO Backend -- Tests: Master Finance (E2, income + transactions)
# =============================================================================
#
# telegram_id range: 90000-90999
#
# Coverage:
#   GET /masters/me/income
#     - sums title-tagged DONE rows in the current calendar period
#     - excludes untitled plumbing rows
#     - delta_pct vs previous period; null when no previous activity
#     - month period
#     - requires verified master (403) / no auth (401)
#   GET /masters/me/transactions
#     - title-tagged rows only; counterparty_name resolved (null for platform)
#     - newest-first; offset/limit pagination
#   record_master_ledger persists title + counterparty_id
# =============================================================================

from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.masters.models import MasterProfile
from app.modules.payments.models import LedgerStatus, MasterLedger
from app.modules.payments.service import record_master_ledger
from app.modules.users.models import User, UserRole
from tests.helpers import auth_headers, login_user

INCOME_URL = "/api/v1/masters/me/income"
TRANSACTIONS_URL = "/api/v1/masters/me/transactions"

_TID_MIN = 90000
_TID_MAX = 90999


# ===================================================================
# Cleanup
# ===================================================================


@pytest.fixture(autouse=True)
async def cleanup(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    """Clean test data before/after each test in FK-safe order."""
    await _do_cleanup(db_session)
    yield
    await _do_cleanup(db_session)


async def _do_cleanup(session: AsyncSession) -> None:
    """Delete all test entities for telegram_id 90000-90999."""
    await session.rollback()

    user_ids_subq = select(User.id).where(
        User.telegram_id.between(_TID_MIN, _TID_MAX),
    )

    # 1. master_ledger -- user_id FK is RESTRICT, so delete before users.
    #    Drop rows owned by OR referencing (counterparty) our users.
    await session.execute(
        MasterLedger.__table__.delete().where(
            MasterLedger.user_id.in_(user_ids_subq),
        )
    )
    await session.execute(
        MasterLedger.__table__.delete().where(
            MasterLedger.counterparty_id.in_(user_ids_subq),
        )
    )
    # 2. audit_logs for our users.
    from app.core.audit import AuditLog
    await session.execute(
        AuditLog.__table__.delete().where(
            AuditLog.actor_id.in_(user_ids_subq),
        )
    )
    # 3. master_profiles (FK -> users).
    await session.execute(
        MasterProfile.__table__.delete().where(
            MasterProfile.user_id.in_(user_ids_subq),
        )
    )
    # 4. users.
    await session.execute(
        User.__table__.delete().where(
            User.telegram_id.between(_TID_MIN, _TID_MAX),
        )
    )
    await session.commit()


# ===================================================================
# Helpers
# ===================================================================


async def _make_verified_master(
    client: AsyncClient,
    db_session: AsyncSession,
    telegram_id: int,
) -> dict:
    """Create a verified master and return the auth dict (with session_token)."""
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
    return auth


async def _add_ledger(
    db_session: AsyncSession,
    user_id: str,
    *,
    amount_cents: int,
    title: str | None = None,
    counterparty_id: str | None = None,
    is_frozen: bool = False,
    created_at: datetime | None = None,
    reason: str = "finance-test",
) -> MasterLedger:
    """Insert a master_ledger row directly (bypasses balance recalc).

    Direct insert lets us control created_at for period boundaries and tag
    title/counterparty without going through the full purchase flow.
    """
    entry = MasterLedger(
        user_id=user_id,
        amount_cents=amount_cents,
        is_frozen=is_frozen,
        status=LedgerStatus.DONE.value,
        reason=reason,
        title=title,
        counterparty_id=counterparty_id,
    )
    if created_at is not None:
        entry.created_at = created_at
    db_session.add(entry)
    await db_session.flush()
    return entry


# ===================================================================
# GET /masters/me/income
# ===================================================================


@pytest.mark.asyncio
async def test_income_sums_titled_in_current_period(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Income = net of title-tagged DONE rows in the current calendar week."""
    master = await _make_verified_master(client, db_session, telegram_id=90001)
    mid = master["user"]["id"]
    now = datetime.now(UTC)

    await _add_ledger(db_session, mid, amount_cents=12000, title="Оплата за практику", created_at=now)
    await _add_ledger(db_session, mid, amount_cents=-2000, title="Комиссия", created_at=now)
    await db_session.commit()

    resp = await client.get(
        INCOME_URL,
        params={"period": "week"},
        headers=auth_headers(master["session_token"]),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["income_cents"] == 10000
    assert data["prev_income_cents"] == 0
    assert data["delta_pct"] is None


@pytest.mark.asyncio
async def test_income_excludes_untitled_plumbing(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Untitled plumbing rows are excluded from income."""
    master = await _make_verified_master(client, db_session, telegram_id=90002)
    mid = master["user"]["id"]
    now = datetime.now(UTC)

    await _add_ledger(db_session, mid, amount_cents=10000, title="Оплата за практику", created_at=now)
    # Untitled reversal/hold plumbing -- must NOT count.
    await _add_ledger(db_session, mid, amount_cents=99999, title=None, created_at=now)
    await db_session.commit()

    resp = await client.get(
        INCOME_URL,
        params={"period": "week"},
        headers=auth_headers(master["session_token"]),
    )
    assert resp.status_code == 200
    assert resp.json()["income_cents"] == 10000


@pytest.mark.asyncio
async def test_income_delta_pct_vs_previous(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """delta_pct compares the current period against the previous one."""
    master = await _make_verified_master(client, db_session, telegram_id=90003)
    mid = master["user"]["id"]
    now = datetime.now(UTC)

    # Current week: +10000. Previous week (now - 7d): +5000.
    await _add_ledger(db_session, mid, amount_cents=10000, title="Оплата за практику", created_at=now)
    await _add_ledger(
        db_session, mid, amount_cents=5000, title="Оплата за практику",
        created_at=now - timedelta(days=7),
    )
    await db_session.commit()

    resp = await client.get(
        INCOME_URL,
        params={"period": "week"},
        headers=auth_headers(master["session_token"]),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["income_cents"] == 10000
    assert data["prev_income_cents"] == 5000
    # (10000 - 5000) / 5000 * 100 = 100
    assert data["delta_pct"] == 100


@pytest.mark.asyncio
async def test_income_delta_pct_null_when_prev_negative(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """S-1: a net-negative previous period yields delta_pct null (no sign flip)."""
    master = await _make_verified_master(client, db_session, telegram_id=90004)
    mid = master["user"]["id"]
    now = datetime.now(UTC)

    # Current week: +10000.
    await _add_ledger(
        db_session, mid, amount_cents=10000,
        title="Оплата за практику", created_at=now,
    )
    # Previous week nets to -2000 (refund exceeded sale).
    await _add_ledger(
        db_session, mid, amount_cents=3000,
        title="Оплата за практику", created_at=now - timedelta(days=7),
    )
    await _add_ledger(
        db_session, mid, amount_cents=-5000,
        title="Возврат", created_at=now - timedelta(days=7),
    )
    await db_session.commit()

    resp = await client.get(
        INCOME_URL,
        params={"period": "week"},
        headers=auth_headers(master["session_token"]),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["income_cents"] == 10000
    assert data["prev_income_cents"] == -2000
    # prev <= 0 -> no meaningful base -> null (old abs() would have flipped sign).
    assert data["delta_pct"] is None


@pytest.mark.asyncio
async def test_income_month_period(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Month period sums the current calendar month only."""
    master = await _make_verified_master(client, db_session, telegram_id=90004)
    mid = master["user"]["id"]
    now = datetime.now(UTC)
    last_month_day = now.replace(day=1) - timedelta(days=1)

    await _add_ledger(db_session, mid, amount_cents=8000, title="Оплата за практику", created_at=now)
    await _add_ledger(
        db_session, mid, amount_cents=3000, title="Оплата за практику",
        created_at=last_month_day,
    )
    await db_session.commit()

    resp = await client.get(
        INCOME_URL,
        params={"period": "month"},
        headers=auth_headers(master["session_token"]),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["income_cents"] == 8000
    assert data["prev_income_cents"] == 3000


@pytest.mark.asyncio
async def test_income_requires_master(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """A regular (non-master) user gets 403."""
    user = await login_user(client, telegram_id=90005, first_name="Plain")
    resp = await client.get(
        INCOME_URL,
        headers=auth_headers(user["session_token"]),
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_income_no_auth(client: AsyncClient) -> None:
    """No auth: 401."""
    resp = await client.get(INCOME_URL)
    assert resp.status_code == 401


# ===================================================================
# GET /masters/me/transactions
# ===================================================================


@pytest.mark.asyncio
async def test_transactions_shape_and_counterparty(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Title-tagged rows only; counterparty resolved, null for platform rows."""
    master = await _make_verified_master(client, db_session, telegram_id=90010)
    mid = master["user"]["id"]
    student = await login_user(client, telegram_id=90011, first_name="Anna")
    sid = student["user"]["id"]
    # Set last_name directly (login_user only takes first_name) to exercise the
    # "First Last" name resolution in the counterparty join.
    student_user = await db_session.get(User, sid)
    student_user.last_name = "K"
    await db_session.flush()
    now = datetime.now(UTC)

    await _add_ledger(
        db_session, mid, amount_cents=12000, title="Оплата за практику",
        counterparty_id=sid, created_at=now,
    )
    await _add_ledger(
        db_session, mid, amount_cents=-2000, title="Комиссия",
        counterparty_id=None, created_at=now - timedelta(minutes=1),
    )
    # Untitled plumbing -- excluded.
    await _add_ledger(db_session, mid, amount_cents=99999, title=None, created_at=now)
    await db_session.commit()

    resp = await client.get(
        TRANSACTIONS_URL,
        headers=auth_headers(master["session_token"]),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2

    by_title = {it["title"]: it for it in data["items"]}
    assert set(by_title) == {"Оплата за практику", "Комиссия"}
    assert by_title["Оплата за практику"]["counterparty_name"] == "Anna K"
    assert by_title["Оплата за практику"]["amount_cents"] == 12000
    assert by_title["Комиссия"]["counterparty_name"] is None
    assert by_title["Комиссия"]["amount_cents"] == -2000

    item = data["items"][0]
    assert set(item.keys()) == {
        "title", "practice_title", "created_at", "counterparty_name", "amount_cents",
    }
    # M5: no practice_id on these direct-insert ledger rows → practice_title None.
    assert item["practice_title"] is None


@pytest.mark.asyncio
async def test_transactions_newest_first(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Transactions are ordered by created_at descending."""
    master = await _make_verified_master(client, db_session, telegram_id=90012)
    mid = master["user"]["id"]
    base = datetime.now(UTC) - timedelta(hours=5)

    await _add_ledger(db_session, mid, amount_cents=100, title="A", created_at=base)
    await _add_ledger(db_session, mid, amount_cents=200, title="B", created_at=base + timedelta(hours=1))
    await _add_ledger(db_session, mid, amount_cents=300, title="C", created_at=base + timedelta(hours=2))
    await db_session.commit()

    resp = await client.get(
        TRANSACTIONS_URL,
        headers=auth_headers(master["session_token"]),
    )
    assert resp.status_code == 200
    titles = [it["title"] for it in resp.json()["items"]]
    assert titles == ["C", "B", "A"]


@pytest.mark.asyncio
async def test_transactions_pagination(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """limit/offset paginate while total reflects the full set."""
    master = await _make_verified_master(client, db_session, telegram_id=90013)
    mid = master["user"]["id"]
    base = datetime.now(UTC) - timedelta(hours=5)
    for i in range(3):
        await _add_ledger(
            db_session, mid, amount_cents=100, title=f"T{i}",
            created_at=base + timedelta(hours=i),
        )
    await db_session.commit()

    headers = auth_headers(master["session_token"])

    p1 = await client.get(TRANSACTIONS_URL, params={"limit": 2, "offset": 0}, headers=headers)
    assert p1.status_code == 200
    assert p1.json()["total"] == 3
    assert len(p1.json()["items"]) == 2

    p2 = await client.get(TRANSACTIONS_URL, params={"limit": 2, "offset": 2}, headers=headers)
    assert p2.status_code == 200
    assert p2.json()["total"] == 3
    assert len(p2.json()["items"]) == 1


@pytest.mark.asyncio
async def test_transactions_requires_master(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """A regular (non-master) user gets 403."""
    user = await login_user(client, telegram_id=90014, first_name="Plain")
    resp = await client.get(
        TRANSACTIONS_URL,
        headers=auth_headers(user["session_token"]),
    )
    assert resp.status_code == 403


# ===================================================================
# record_master_ledger persists the new columns
# ===================================================================


@pytest.mark.asyncio
async def test_record_master_ledger_persists_title_counterparty(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """record_master_ledger writes title + counterparty_id onto the row."""
    master = await _make_verified_master(client, db_session, telegram_id=90020)
    mid = master["user"]["id"]
    student = await login_user(client, telegram_id=90021, first_name="Bob")
    sid = student["user"]["id"]

    entry = await record_master_ledger(
        user_id=mid,
        amount_cents=5000,
        reason="sale:practice=test",
        is_frozen=True,
        session=db_session,
        title="Оплата за практику",
        counterparty_id=sid,
    )
    await db_session.commit()

    fetched = await db_session.get(MasterLedger, entry.id)
    assert fetched is not None
    assert fetched.title == "Оплата за практику"
    assert str(fetched.counterparty_id) == sid
