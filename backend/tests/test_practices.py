# =============================================================================
# Test: Practices -- CRUD + Pricing + Public Feed (Phase 4.2 + 4.3/4.4)
# =============================================================================
#
# telegram_id ranges:
#   60001-60099 -- master users
#   60100-60199 -- regular users (non-master)
#   60900-60999 -- admin users
# =============================================================================

from collections.abc import AsyncGenerator
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import User, UserRole
from tests.helpers import auth_headers, login_user, full_cleanup_range

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
PRACTICES_URL = "/api/v1/practices"
MY_PRACTICES_URL = "/api/v1/masters/me/practices"
APPLY_URL = "/api/v1/masters/apply"
VERIFY_URL = "/api/v1/admin/masters/{user_id}/verify"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
async def cleanup(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    """Clean all test data before/after each test (TD-032: ORM, no raw SQL)."""
    await _do_cleanup(db_session)
    yield
    await _do_cleanup(db_session)


async def _do_cleanup(session: AsyncSession) -> None:
    """Full ORM cleanup for telegram_id 60000-60999."""
    await full_cleanup_range(session, 60000, 60999, delete_users=False)
    await session.commit()



# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _valid_practice_body(**overrides: object) -> dict:
    """Return a valid CreatePracticeRequest body."""
    base: dict = {
        "practice_type": "live",
        "title": "Morning Meditation",
        "description": "Guided breathwork session",
        "scheduled_at": (
            datetime.now(timezone.utc) + timedelta(days=7)
        ).isoformat(),
        "duration_minutes": 60,
        "timezone": "Europe/Moscow",
        "max_participants": 20,
        "is_free": True,
        "price_cents": 0,
        "currency": "EUR",
    }
    base.update(overrides)
    return base


def _valid_apply_body() -> dict:
    """Return a valid MasterApplyRequest body."""
    return {
        "profile": {
            "display_name": "Test Master",
            "email": "master@test.com",
        },
        "experience": {
            "methods": ["meditation"],
            "experience_years": 5,
            "bio": "Experienced practitioner",
        },
        "documents": [],
    }


async def _make_verified_master(
    client: AsyncClient,
    db_session: AsyncSession,
    telegram_id: int = 60001,
) -> dict:
    """Create user, apply as master, verify via admin.

    Returns auth data with role=master.
    """
    # Create user and submit application.
    auth = await login_user(
        client, telegram_id=telegram_id, first_name="Master",
    )
    await client.post(
        APPLY_URL,
        json=_valid_apply_body(),
        headers=auth_headers(auth["session_token"]),
    )

    # Promote admin user (telegram_id=60900).
    admin_auth = await login_user(
        client, telegram_id=60900, first_name="Admin",
    )
    await db_session.execute(
    update(User)
    .where(User.telegram_id == 60900)
    .values(role=UserRole.ADMIN.value)
)
    await db_session.commit()

    # Re-login admin to pick up new role in session.
    admin_auth = await login_user(
        client, telegram_id=60900, first_name="Admin",
    )

    user_id = auth["user"]["id"]
    verify_resp = await client.post(
        VERIFY_URL.format(user_id=user_id),
        json={},
        headers=auth_headers(admin_auth["session_token"]),
    )
    assert verify_resp.status_code == 200

    # Re-login to pick up master role in session.
    auth = await login_user(
        client, telegram_id=telegram_id, first_name="Master",
    )
    return auth


async def _create_and_publish(
    client: AsyncClient,
    auth: dict,
    **overrides: object,
) -> str:
    """Create a practice and transition status to scheduled.

    Returns practice_id.
    """
    body = _valid_practice_body(**overrides)
    create_resp = await client.post(
        PRACTICES_URL,
        json=body,
        headers=auth_headers(auth["session_token"]),
    )
    assert create_resp.status_code == 201
    practice_id = create_resp.json()["id"]

    patch_resp = await client.patch(
        f"{PRACTICES_URL}/{practice_id}",
        json={"status": "scheduled"},
        headers=auth_headers(auth["session_token"]),
    )
    assert patch_resp.status_code == 200
    return practice_id


# ===================================================================
# PHASE 4.2 TESTS -- CRUD
# ===================================================================


# ---------------------------------------------------------------------------
# POST /practices -- success
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_create_practice_success(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Verified master can create a practice."""
    auth = await _make_verified_master(client, db_session)

    resp = await client.post(
        PRACTICES_URL,
        json=_valid_practice_body(),
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Morning Meditation"
    assert data["status"] == "draft"
    assert data["is_free"] is True
    assert data["price_cents"] == 0
    assert data["currency"] == "EUR"


# ---------------------------------------------------------------------------
# POST /practices -- not a master (403)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_create_practice_not_master(
    client: AsyncClient,
) -> None:
    """Regular user cannot create practice: 403."""
    auth = await login_user(
        client, telegram_id=60101, first_name="User",
    )
    resp = await client.post(
        PRACTICES_URL,
        json=_valid_practice_body(),
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# POST /practices -- no auth (401)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_create_practice_no_auth(
    client: AsyncClient,
) -> None:
    """No auth token: 401."""
    resp = await client.post(PRACTICES_URL, json=_valid_practice_body())
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# POST /practices -- invalid duration (422)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_create_practice_invalid_duration(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Duration out of allowed range: 422."""
    auth = await _make_verified_master(client, db_session)

    body = _valid_practice_body(duration_minutes=9999)
    resp = await client.post(
        PRACTICES_URL,
        json=body,
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /practices/{id} -- success
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_get_practice_success(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Any authenticated user can view a scheduled practice."""
    master_auth = await _make_verified_master(client, db_session)

    practice_id = await _create_and_publish(client, master_auth)

    user_auth = await login_user(
        client, telegram_id=60101, first_name="Viewer",
    )
    resp = await client.get(
        f"{PRACTICES_URL}/{practice_id}",
        headers=auth_headers(user_auth["session_token"]),
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == practice_id


# ---------------------------------------------------------------------------
# GET /practices/{id} -- draft hidden from non-owner (404)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_get_practice_draft_hidden(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Draft practice invisible to non-owner: 404."""
    master_auth = await _make_verified_master(client, db_session)

    create_resp = await client.post(
        PRACTICES_URL,
        json=_valid_practice_body(),
        headers=auth_headers(master_auth["session_token"]),
    )
    assert create_resp.status_code == 201
    practice_id = create_resp.json()["id"]

    user_auth = await login_user(
        client, telegram_id=60102, first_name="Stranger",
    )
    resp = await client.get(
        f"{PRACTICES_URL}/{practice_id}",
        headers=auth_headers(user_auth["session_token"]),
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# PATCH /practices/{id} -- success
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_update_practice_success(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Master can update their own practice."""
    auth = await _make_verified_master(client, db_session)

    create_resp = await client.post(
        PRACTICES_URL,
        json=_valid_practice_body(),
        headers=auth_headers(auth["session_token"]),
    )
    assert create_resp.status_code == 201
    practice_id = create_resp.json()["id"]

    resp = await client.patch(
        f"{PRACTICES_URL}/{practice_id}",
        json={"title": "Evening Yoga"},
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Evening Yoga"


# ---------------------------------------------------------------------------
# PATCH /practices/{id} -- not owner (404, P-08)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_update_practice_not_owner(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Non-owner master cannot update practice: 404 (P-08)."""
    master_auth = await _make_verified_master(
        client, db_session, telegram_id=60002,
    )

    create_resp = await client.post(
        PRACTICES_URL,
        json=_valid_practice_body(),
        headers=auth_headers(master_auth["session_token"]),
    )
    assert create_resp.status_code == 201
    practice_id = create_resp.json()["id"]

    other_auth = await _make_verified_master(
        client, db_session, telegram_id=60003,
    )

    resp = await client.patch(
        f"{PRACTICES_URL}/{practice_id}",
        json={"title": "Hijacked"},
        headers=auth_headers(other_auth["session_token"]),
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /practices/{id} -- draft success
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_delete_draft_practice(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Master can delete a draft practice (status -> deleted)."""
    auth = await _make_verified_master(client, db_session)

    create_resp = await client.post(
        PRACTICES_URL,
        json=_valid_practice_body(),
        headers=auth_headers(auth["session_token"]),
    )
    assert create_resp.status_code == 201
    practice_id = create_resp.json()["id"]

    resp = await client.delete(
        f"{PRACTICES_URL}/{practice_id}",
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "deleted"


# ---------------------------------------------------------------------------
# DELETE /practices/{id} -- non-draft (400)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_delete_non_draft_practice(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Cannot delete a scheduled practice: 400."""
    auth = await _make_verified_master(client, db_session)

    practice_id = await _create_and_publish(client, auth)

    resp = await client.delete(
        f"{PRACTICES_URL}/{practice_id}",
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# DELETE /practices/{id} -- not owner (404, P-08)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_delete_practice_not_owner(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Non-owner master cannot delete practice: 404 (P-08)."""
    master_auth = await _make_verified_master(
        client, db_session, telegram_id=60006,
    )

    create_resp = await client.post(
        PRACTICES_URL,
        json=_valid_practice_body(),
        headers=auth_headers(master_auth["session_token"]),
    )
    assert create_resp.status_code == 201
    practice_id = create_resp.json()["id"]

    other_auth = await _make_verified_master(
        client, db_session, telegram_id=60007,
    )

    resp = await client.delete(
        f"{PRACTICES_URL}/{practice_id}",
        headers=auth_headers(other_auth["session_token"]),
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# PATCH /practices/{id} -- invalid status transition (400)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_update_practice_invalid_transition(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Cannot transition from draft to completed: 400."""
    auth = await _make_verified_master(client, db_session)

    create_resp = await client.post(
        PRACTICES_URL,
        json=_valid_practice_body(),
        headers=auth_headers(auth["session_token"]),
    )
    assert create_resp.status_code == 201
    practice_id = create_resp.json()["id"]

    resp = await client.patch(
        f"{PRACTICES_URL}/{practice_id}",
        json={"status": "completed"},
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# PATCH /practices/{id} -- null NOT NULL field (400, P-02)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_update_practice_null_not_null_field(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Setting NOT NULL field to null: 400."""
    auth = await _make_verified_master(client, db_session)

    create_resp = await client.post(
        PRACTICES_URL,
        json=_valid_practice_body(),
        headers=auth_headers(auth["session_token"]),
    )
    assert create_resp.status_code == 201
    practice_id = create_resp.json()["id"]

    resp = await client.patch(
        f"{PRACTICES_URL}/{practice_id}",
        json={"scheduled_at": None},
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# GET /masters/me/practices -- success
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_list_master_practices(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Master sees their own practices (excluding deleted).

    R-04: response is now PaginatedPracticesResponse with total/limit/offset.
    """
    auth = await _make_verified_master(client, db_session)

    # Create 2 practices.
    for _ in range(2):
        r = await client.post(
            PRACTICES_URL,
            json=_valid_practice_body(),
            headers=auth_headers(auth["session_token"]),
        )
        assert r.status_code == 201

    resp = await client.get(
        MY_PRACTICES_URL,
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert "limit" in data
    assert "offset" in data


# ===================================================================
# PHASE 4.3/4.4 TESTS -- PRICING
# ===================================================================


# ---------------------------------------------------------------------------
# POST /practices -- paid practice success
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_create_paid_practice(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Master creates a paid practice: is_free=False, price > 0."""
    auth = await _make_verified_master(client, db_session)

    resp = await client.post(
        PRACTICES_URL,
        json=_valid_practice_body(
            is_free=False,
            price_cents=1500,
        ),
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["is_free"] is False
    assert data["price_cents"] == 1500
    assert data["currency"] == "EUR"


# ---------------------------------------------------------------------------
# POST /practices -- free forces price_cents=0
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_create_free_practice_forces_zero_price(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """is_free=True forces price_cents=0 even if client sends 500."""
    auth = await _make_verified_master(client, db_session)

    resp = await client.post(
        PRACTICES_URL,
        json=_valid_practice_body(
            is_free=True,
            price_cents=500,
        ),
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 201
    assert resp.json()["price_cents"] == 0


# ---------------------------------------------------------------------------
# POST /practices -- paid with price=0 (400)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_create_paid_practice_zero_price(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """is_free=False with price_cents=0: 400."""
    auth = await _make_verified_master(client, db_session)

    resp = await client.post(
        PRACTICES_URL,
        json=_valid_practice_body(
            is_free=False,
            price_cents=0,
        ),
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# PATCH /practices -- change to paid
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_update_practice_to_paid(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Master changes free practice to paid via PATCH."""
    auth = await _make_verified_master(client, db_session)

    create_resp = await client.post(
        PRACTICES_URL,
        json=_valid_practice_body(),
        headers=auth_headers(auth["session_token"]),
    )
    assert create_resp.status_code == 201
    practice_id = create_resp.json()["id"]

    resp = await client.patch(
        f"{PRACTICES_URL}/{practice_id}",
        json={"is_free": False, "price_cents": 2000},
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 200
    assert resp.json()["is_free"] is False
    assert resp.json()["price_cents"] == 2000


# ---------------------------------------------------------------------------
# PATCH /practices -- set is_free=True forces price to 0
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_update_practice_to_free_zeroes_price(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Setting is_free=True on a paid practice zeroes price_cents."""
    auth = await _make_verified_master(client, db_session)

    create_resp = await client.post(
        PRACTICES_URL,
        json=_valid_practice_body(
            is_free=False,
            price_cents=2000,
        ),
        headers=auth_headers(auth["session_token"]),
    )
    assert create_resp.status_code == 201
    practice_id = create_resp.json()["id"]

    resp = await client.patch(
        f"{PRACTICES_URL}/{practice_id}",
        json={"is_free": True},
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 200
    assert resp.json()["is_free"] is True
    assert resp.json()["price_cents"] == 0


# ===================================================================
# PHASE 4.3 TESTS -- PUBLIC FEED
# ===================================================================


# ---------------------------------------------------------------------------
# GET /practices -- basic list (only scheduled/live)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_list_practices_public(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Public feed returns only scheduled/live practices.

    Scoped to this test's master via master_id filter to stay
    independent of seed data present in the database.
    """
    auth = await _make_verified_master(client, db_session)
    master_id = auth["user"]["id"]

    # Create 1 draft (should NOT appear) and 1 scheduled.
    await client.post(
        PRACTICES_URL,
        json=_valid_practice_body(title="Draft"),
        headers=auth_headers(auth["session_token"]),
    )
    await _create_and_publish(
        client, auth, title="Published",
    )

    user_auth = await login_user(
        client, telegram_id=60103, first_name="Viewer",
    )
    resp = await client.get(
        f"{PRACTICES_URL}?master_id={master_id}",
        headers=auth_headers(user_auth["session_token"]),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Published"
    assert "limit" in data
    assert "offset" in data


# ---------------------------------------------------------------------------
# GET /practices -- filter by practice_type
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_list_practices_filter_type(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Filter by practice_type returns only matching.

    Scoped to this test's master via master_id filter to stay
    independent of seed data present in the database.
    """
    auth = await _make_verified_master(client, db_session)
    master_id = auth["user"]["id"]

    await _create_and_publish(
        client, auth, practice_type="live", title="Live",
    )
    await _create_and_publish(
        client, auth,
        practice_type="one_on_one",
        title="OneOnOne",
    )

    user_auth = await login_user(
        client, telegram_id=60104, first_name="Viewer",
    )
    resp = await client.get(
        f"{PRACTICES_URL}?practice_type=live&master_id={master_id}",
        headers=auth_headers(user_auth["session_token"]),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Live"


# ---------------------------------------------------------------------------
# GET /practices -- filter by master_id
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_list_practices_filter_master(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Filter by master_id returns only their practices."""
    master1 = await _make_verified_master(
        client, db_session, telegram_id=60004,
    )
    master2 = await _make_verified_master(
        client, db_session, telegram_id=60005,
    )

    await _create_and_publish(
        client, master1, title="M1 Practice",
    )
    await _create_and_publish(
        client, master2, title="M2 Practice",
    )

    m1_id = master1["user"]["id"]
    user_auth = await login_user(
        client, telegram_id=60105, first_name="Viewer",
    )
    resp = await client.get(
        f"{PRACTICES_URL}?master_id={m1_id}",
        headers=auth_headers(user_auth["session_token"]),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "M1 Practice"


# ---------------------------------------------------------------------------
# GET /practices -- sort by price_cents
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_list_practices_sort_price(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Sort by price_cents ascending.

    Scoped to this test's master via master_id filter to stay
    independent of seed data present in the database.
    """
    auth = await _make_verified_master(client, db_session)
    master_id = auth["user"]["id"]

    await _create_and_publish(
        client, auth,
        title="Expensive",
        is_free=False,
        price_cents=5000,
    )
    await _create_and_publish(
        client, auth,
        title="Cheap",
        is_free=False,
        price_cents=500,
    )
    await _create_and_publish(
        client, auth,
        title="Free",
        is_free=True,
    )

    user_auth = await login_user(
        client, telegram_id=60106, first_name="Viewer",
    )
    resp = await client.get(
        f"{PRACTICES_URL}?sort_by=price_cents&sort_order=asc&master_id={master_id}",
        headers=auth_headers(user_auth["session_token"]),
    )
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) == 3
    prices = [i["price_cents"] for i in items]
    assert prices == sorted(prices)


# ---------------------------------------------------------------------------
# GET /practices -- pagination
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_list_practices_pagination(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Pagination limit/offset works correctly.

    Scoped to this test's master via master_id filter to stay
    independent of seed data present in the database.
    """
    auth = await _make_verified_master(client, db_session)
    master_id = auth["user"]["id"]

    for i in range(3):
        await _create_and_publish(
            client, auth, title=f"Practice {i}",
        )

    user_auth = await login_user(
        client, telegram_id=60107, first_name="Viewer",
    )
    resp = await client.get(
        f"{PRACTICES_URL}?master_id={master_id}&limit=2&offset=0",
        headers=auth_headers(user_auth["session_token"]),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3
    assert len(data["items"]) == 2
    assert data["limit"] == 2
    assert data["offset"] == 0

    # Page 2.
    resp2 = await client.get(
        f"{PRACTICES_URL}?master_id={master_id}&limit=2&offset=2",
        headers=auth_headers(user_auth["session_token"]),
    )
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert len(data2["items"]) == 1


# ---------------------------------------------------------------------------
# GET /practices -- no auth (401)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_list_practices_no_auth(
    client: AsyncClient,
) -> None:
    """Public feed requires authentication: 401."""
    resp = await client.get(PRACTICES_URL)
    assert resp.status_code == 401
