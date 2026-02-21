# =============================================================================
# Test: Admin Withdrawals -- approve, reject, list (Phase 6.6, Batch 3)
# =============================================================================
#
# telegram_id ranges:
#   78001-78099 -- masters
#   78900-78999 -- admins
# =============================================================================

from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.payments.models import Payment, PaymentDirection, PaymentStatus
from tests.helpers import auth_headers, login_user

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
APPLY_URL = "/api/v1/masters/apply"
VERIFY_URL = "/api/v1/admin/masters/{user_id}/verify"
PAYOUT_URL = "/api/v1/masters/me/payout"
WITHDRAW_URL = "/api/v1/masters/me/withdraw"
ADMIN_WITHDRAWALS_URL = "/api/v1/admin/withdrawals"

# ---------------------------------------------------------------------------
# Cleanup (dependency order: audit -> company_ledger -> master_ledger ->
#   payments -> withdrawals -> master_profiles -> reset users -> delete users)
# ---------------------------------------------------------------------------
_TID_RANGE = (
    "SELECT id FROM users WHERE telegram_id BETWEEN 78000 AND 78999"
)

_CLEANUP_QUERIES = [
    # 1. Audit logs referencing our users.
    text(
        "DELETE FROM audit_logs WHERE actor_id IN (" + _TID_RANGE + ")"
    ),
    # 2. Company ledger (withdrawal fees reference our withdrawals).
    text(
        "DELETE FROM company_ledger WHERE reason LIKE 'withdrawal%%'"
    ),
    # 3. Master ledger.
    text(
        "DELETE FROM master_ledger WHERE user_id IN (" + _TID_RANGE + ")"
    ),
    # 4. Payments (OUT records from approve).
    text(
        "DELETE FROM payments WHERE user_id IN (" + _TID_RANGE + ")"
    ),
    # 5. Withdrawals.
    text(
        "DELETE FROM withdrawals WHERE user_id IN (" + _TID_RANGE + ")"
    ),
    # 6. Master profiles.
    text(
        "DELETE FROM master_profiles WHERE user_id IN (" + _TID_RANGE + ")"
    ),
    # 7. Reset roles and balance.
    text(
        "UPDATE users SET role = 'user', balance_cents = 0 "
        "WHERE telegram_id BETWEEN 78000 AND 78999"
    ),
    # 8. Delete users.
    text(
        "DELETE FROM users WHERE telegram_id BETWEEN 78000 AND 78999"
    ),
]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
async def cleanup(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    """Clean up test data before and after each test."""
    for q in _CLEANUP_QUERIES:
        await db_session.execute(q)
    await db_session.commit()
    yield
    for q in _CLEANUP_QUERIES:
        await db_session.execute(q)
    await db_session.commit()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
async def _make_verified_master(
    client: AsyncClient,
    db_session: AsyncSession,
    telegram_id: int = 78001,
) -> dict:
    """Create user, apply as master, verify via admin. Returns session info."""
    auth = await login_user(client, telegram_id=telegram_id)
    token = auth["session_token"]

    await client.post(
        APPLY_URL,
        json={
            "profile": {
                "display_name": f"Master {telegram_id}",
                "email": f"m{telegram_id}@test.com",
            },
            "experience": {
                "methods": ["meditation"],
                "experience_years": 5,
            },
        },
        headers=auth_headers(token),
    )

    user_id = auth["user"]["id"]

    # Create admin and verify.
    admin_auth = await login_user(client, telegram_id=78900)
    await db_session.execute(
        text("UPDATE users SET role = 'admin' WHERE telegram_id = 78900"),
    )
    await db_session.commit()
    admin_auth = await login_user(client, telegram_id=78900)

    verify_resp = await client.post(
        VERIFY_URL.format(user_id=user_id),
        json={},
        headers=auth_headers(admin_auth["session_token"]),
    )
    assert verify_resp.status_code == 200

    # Re-login master to pick up role=master.
    auth = await login_user(client, telegram_id=telegram_id)
    return {
        "session_token": auth["session_token"],
        "user_id": user_id,
        "telegram_id": telegram_id,
    }


async def _make_admin(
    client: AsyncClient,
    db_session: AsyncSession,
    telegram_id: int = 78901,
) -> dict:
    """Create a separate admin for approve/reject actions."""
    auth = await login_user(client, telegram_id=telegram_id)
    await db_session.execute(
        text(
            "UPDATE users SET role = 'admin' "
            f"WHERE telegram_id = {telegram_id}"
        ),
    )
    await db_session.commit()
    auth = await login_user(client, telegram_id=telegram_id)
    return {
        "session_token": auth["session_token"],
        "user_id": auth["user"]["id"],
    }


async def _give_available_balance(
    db_session: AsyncSession,
    user_id: str,
    amount: int,
) -> None:
    """Insert a master_ledger credit (available, not frozen)."""
    from app.modules.payments.service import record_master_ledger

    await record_master_ledger(
        user_id=user_id,
        amount_cents=amount,
        reason="test_credit",
        is_frozen=False,
        session=db_session,
    )
    await db_session.commit()


async def _set_payout_and_withdraw(
    client: AsyncClient,
    db_session: AsyncSession,
    master: dict,
    amount_cents: int = 5000,
) -> str:
    """Set payout details, give balance, create withdrawal.

    Returns withdrawal id.
    """
    # Set payout details.
    resp = await client.patch(
        PAYOUT_URL,
        json={
            "method": "bank_transfer",
            "details": {"iban": "DE89370400440532013000"},
        },
        headers=auth_headers(master["session_token"]),
    )
    assert resp.status_code == 200

    # Give balance.
    await _give_available_balance(db_session, master["user_id"], amount_cents * 2)

    # Create withdrawal.
    resp = await client.post(
        WITHDRAW_URL,
        json={"amount_cents": amount_cents},
        headers=auth_headers(master["session_token"]),
    )
    assert resp.status_code == 201
    return resp.json()["id"]


# ===================================================================
# APPROVE
# ===================================================================


@pytest.mark.asyncio
async def test_approve_withdrawal_success(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Admin approves pending withdrawal: status=approved, frozen debited."""
    master = await _make_verified_master(client, db_session)
    withdrawal_id = await _set_payout_and_withdraw(client, db_session, master)
    admin = await _make_admin(client, db_session)

    resp = await client.post(
        f"{ADMIN_WITHDRAWALS_URL}/{withdrawal_id}/approve",
        json={"note": "Looks good"},
        headers=auth_headers(admin["session_token"]),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "approved"
    assert data["admin_id"] == admin["user_id"]
    assert data["admin_note"] == "Looks good"
    assert data["approved_at"] is not None


@pytest.mark.asyncio
async def test_approve_double_entry_balanced(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """After approve: SUM(master_ledger + company_ledger) + Payment(OUT) = 0."""
    master = await _make_verified_master(client, db_session)
    withdrawal_id = await _set_payout_and_withdraw(client, db_session, master)
    admin = await _make_admin(client, db_session)

    resp = await client.post(
        f"{ADMIN_WITHDRAWALS_URL}/{withdrawal_id}/approve",
        json={},
        headers=auth_headers(admin["session_token"]),
    )
    assert resp.status_code == 200

    # Verify: master frozen=0, available=5000 (had 10000, withdrew 5000).
    db_session.expire_all()
    row = (await db_session.execute(
        text(
            "SELECT "
            "  COALESCE(SUM(CASE WHEN is_frozen THEN amount_cents ELSE 0 END), 0) AS frozen, "
            "  COALESCE(SUM(CASE WHEN NOT is_frozen THEN amount_cents ELSE 0 END), 0) AS available "
            "FROM master_ledger WHERE user_id = :uid AND status = 'done'"
        ),
        {"uid": master["user_id"]},
    )).one()
    assert row.frozen == 0, f"frozen should be 0 after approve, got {row.frozen}"
    assert row.available == 5000, f"available should be 5000, got {row.available}"

    # Verify: company_ledger has fee entry.
    fee_row = (await db_session.execute(
        text(
            "SELECT COALESCE(SUM(amount_cents), 0) AS total "
            "FROM company_ledger WHERE reason LIKE :reason"
        ),
        {"reason": f"withdrawal_approved:{withdrawal_id}"},
    )).one()
    assert fee_row.total == settings.withdrawal_fee_cents

    # Verify: Payment(OUT) exists.
    pmt_row = (await db_session.execute(
        text(
            "SELECT direction, amount_cents, status FROM payments "
            "WHERE user_id = :uid AND direction = 'out'"
        ),
        {"uid": master["user_id"]},
    )).one()
    assert pmt_row.direction == "out"
    assert pmt_row.amount_cents == 5000 - settings.withdrawal_fee_cents
    assert pmt_row.status == "confirmed"


@pytest.mark.asyncio
async def test_approve_not_pending(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Approve already-approved withdrawal: 409."""
    master = await _make_verified_master(client, db_session)
    withdrawal_id = await _set_payout_and_withdraw(client, db_session, master)
    admin = await _make_admin(client, db_session)

    # First approve.
    resp1 = await client.post(
        f"{ADMIN_WITHDRAWALS_URL}/{withdrawal_id}/approve",
        json={},
        headers=auth_headers(admin["session_token"]),
    )
    assert resp1.status_code == 200

    # Second approve.
    resp2 = await client.post(
        f"{ADMIN_WITHDRAWALS_URL}/{withdrawal_id}/approve",
        json={},
        headers=auth_headers(admin["session_token"]),
    )
    assert resp2.status_code == 409


# ===================================================================
# REJECT
# ===================================================================


@pytest.mark.asyncio
async def test_reject_withdrawal_success(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Admin rejects pending withdrawal: status=rejected, funds unfrozen."""
    master = await _make_verified_master(client, db_session)
    withdrawal_id = await _set_payout_and_withdraw(client, db_session, master)
    admin = await _make_admin(client, db_session)

    resp = await client.post(
        f"{ADMIN_WITHDRAWALS_URL}/{withdrawal_id}/reject",
        json={"note": "Missing IBAN"},
        headers=auth_headers(admin["session_token"]),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "rejected"
    assert data["admin_note"] == "Missing IBAN"
    assert data["rejected_at"] is not None


@pytest.mark.asyncio
async def test_reject_unfreezes_balance(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """After reject: frozen=0, available restored to full amount."""
    master = await _make_verified_master(client, db_session)
    withdrawal_id = await _set_payout_and_withdraw(client, db_session, master)
    admin = await _make_admin(client, db_session)

    resp = await client.post(
        f"{ADMIN_WITHDRAWALS_URL}/{withdrawal_id}/reject",
        json={"note": "Bad details"},
        headers=auth_headers(admin["session_token"]),
    )
    assert resp.status_code == 200

    # Check master profile: frozen=0, available=10000 (fully restored).
    db_session.expire_all()
    row = (await db_session.execute(
        text(
            "SELECT "
            "  COALESCE(SUM(CASE WHEN is_frozen THEN amount_cents ELSE 0 END), 0) AS frozen, "
            "  COALESCE(SUM(CASE WHEN NOT is_frozen THEN amount_cents ELSE 0 END), 0) AS available "
            "FROM master_ledger WHERE user_id = :uid AND status = 'done'"
        ),
        {"uid": master["user_id"]},
    )).one()
    assert row.frozen == 0
    assert row.available == 10000  # Initial 10000 fully restored.


@pytest.mark.asyncio
async def test_reject_not_pending(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Reject already-rejected withdrawal: 409."""
    master = await _make_verified_master(client, db_session)
    withdrawal_id = await _set_payout_and_withdraw(client, db_session, master)
    admin = await _make_admin(client, db_session)

    resp1 = await client.post(
        f"{ADMIN_WITHDRAWALS_URL}/{withdrawal_id}/reject",
        json={"note": "No"},
        headers=auth_headers(admin["session_token"]),
    )
    assert resp1.status_code == 200

    resp2 = await client.post(
        f"{ADMIN_WITHDRAWALS_URL}/{withdrawal_id}/reject",
        json={"note": "No again"},
        headers=auth_headers(admin["session_token"]),
    )
    assert resp2.status_code == 409


# ===================================================================
# AUTH & NOT FOUND
# ===================================================================


@pytest.mark.asyncio
async def test_approve_not_found(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Approve nonexistent withdrawal: 404."""
    admin = await _make_admin(client, db_session)
    fake_id = str(uuid4())
    resp = await client.post(
        f"{ADMIN_WITHDRAWALS_URL}/{fake_id}/approve",
        json={},
        headers=auth_headers(admin["session_token"]),
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_approve_not_admin(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Non-admin cannot approve: 403."""
    master = await _make_verified_master(client, db_session)
    withdrawal_id = await _set_payout_and_withdraw(client, db_session, master)

    resp = await client.post(
        f"{ADMIN_WITHDRAWALS_URL}/{withdrawal_id}/approve",
        json={},
        headers=auth_headers(master["session_token"]),
    )
    assert resp.status_code == 403


# ===================================================================
# LIST
# ===================================================================


@pytest.mark.asyncio
async def test_list_withdrawals_admin(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Admin can list all withdrawals."""
    master = await _make_verified_master(client, db_session)
    await _set_payout_and_withdraw(client, db_session, master, amount_cents=5000)
    admin = await _make_admin(client, db_session)

    resp = await client.get(
        ADMIN_WITHDRAWALS_URL,
        headers=auth_headers(admin["session_token"]),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_list_withdrawals_filter_status(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Admin can filter withdrawals by status."""
    master = await _make_verified_master(client, db_session)
    withdrawal_id = await _set_payout_and_withdraw(client, db_session, master)
    admin = await _make_admin(client, db_session)

    # Approve it.
    await client.post(
        f"{ADMIN_WITHDRAWALS_URL}/{withdrawal_id}/approve",
        json={},
        headers=auth_headers(admin["session_token"]),
    )

    # Filter: pending should not include the approved one.
    resp = await client.get(
        f"{ADMIN_WITHDRAWALS_URL}?status=pending",
        headers=auth_headers(admin["session_token"]),
    )
    assert resp.status_code == 200
    ids = [item["id"] for item in resp.json()["items"]]
    assert withdrawal_id not in ids

    # Filter: approved should include it.
    resp2 = await client.get(
        f"{ADMIN_WITHDRAWALS_URL}?status=approved",
        headers=auth_headers(admin["session_token"]),
    )
    assert resp2.status_code == 200
    ids2 = [item["id"] for item in resp2.json()["items"]]
    assert withdrawal_id in ids2
