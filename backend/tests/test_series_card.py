# =============================================================================
# Test: Practice Series -- card meta (E3, Batch 2)
# =============================================================================
#
# recurrence_days / total_sessions / completed_sessions on PracticeResponse:
#   - present for a series whose ROOT carries a recurrence spec (daily -> the
#     full week [1..7]; weekly/biweekly -> the spec's days);
#   - None for a non-series practice and for a series tag without a spec;
#   - total counts the series' occurrences excluding cancelled, completed counts
#     status=completed -- the same trio for every occurrence of the series;
#   - surfaced by the master list + detail endpoints, NOT the public feed;
#   - resolved in two bounded queries (N+1 guard).
#
# telegram_id range (own cleanup band):
#   62001 -- master, 62900 -- admin
# =============================================================================

from collections.abc import AsyncGenerator
from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.practices.models import Practice, PracticeStatus
from app.modules.users.models import User, UserRole
from tests.helpers import auth_headers, login_user, full_cleanup_range

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
PRACTICES_URL = "/api/v1/practices"
MY_PRACTICES_URL = "/api/v1/masters/me/practices"
APPLY_URL = "/api/v1/masters/apply"
VERIFY_URL = "/api/v1/admin/masters/{user_id}/verify"

_MASTER_TID = 62001
_ADMIN_TID = 62900


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
async def cleanup(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    """Clean all test data before/after each test (ORM, no raw SQL)."""
    await _do_cleanup(db_session)
    yield
    await _do_cleanup(db_session)


async def _do_cleanup(session: AsyncSession) -> None:
    """Full ORM cleanup for telegram_id 62000-62999."""
    await full_cleanup_range(session, 62000, 62999, delete_users=False)
    await session.commit()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _valid_apply_body() -> dict:
    return {
        "profile": {"display_name": "Card Master", "email": "card@test.com"},
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
    telegram_id: int = _MASTER_TID,
) -> dict:
    """Create user, apply as master, verify via admin. Returns master auth."""
    auth = await login_user(
        client, telegram_id=telegram_id, first_name="Master",
    )
    await client.post(
        APPLY_URL,
        json=_valid_apply_body(),
        headers=auth_headers(auth["session_token"]),
    )

    await login_user(client, telegram_id=_ADMIN_TID, first_name="Admin")
    await db_session.execute(
        update(User)
        .where(User.telegram_id == _ADMIN_TID)
        .values(role=UserRole.ADMIN.value)
    )
    await db_session.commit()
    admin_auth = await login_user(
        client, telegram_id=_ADMIN_TID, first_name="Admin",
    )

    user_id = auth["user"]["id"]
    verify_resp = await client.post(
        VERIFY_URL.format(user_id=user_id),
        json={},
        headers=auth_headers(admin_auth["session_token"]),
    )
    assert verify_resp.status_code == 200

    return await login_user(
        client, telegram_id=telegram_id, first_name="Master",
    )


def _valid_practice_body(**overrides: object) -> dict:
    """A valid CreatePracticeRequest body (UTC tz by default)."""
    base: dict = {
        "practice_type": "live",
        "direction": "meditation",
        "difficulty": "beginner",
        "title": "Card Practice",
        "description": "Guided session",
        "scheduled_at": (
            datetime.now(timezone.utc) + timedelta(days=8)
        ).isoformat(),
        "duration_minutes": 60,
        "timezone": "UTC",
        "max_participants": 20,
        "is_free": True,
        "price_cents": 0,
        "currency": "eur",
    }
    base.update(overrides)
    return base


async def _create_and_publish(
    client: AsyncClient,
    auth: dict,
    *,
    recurrence: dict | None = None,
    **overrides: object,
) -> str:
    """Create a practice (optionally a series) and publish it. Returns its id."""
    body = _valid_practice_body(**overrides)
    if recurrence is not None:
        body["recurrence"] = recurrence
        # A recurrence implies a series; set the type unless the caller pinned
        # it explicitly (the batch-1 validator rejects recurrence on non-series).
        if "practice_type" not in overrides:
            body["practice_type"] = "series"
    create = await client.post(
        PRACTICES_URL,
        json=body,
        headers=auth_headers(auth["session_token"]),
    )
    assert create.status_code == 201, create.text
    pid = create.json()["id"]

    patch = await client.patch(
        f"{PRACTICES_URL}/{pid}",
        json={"status": "scheduled"},
        headers=auth_headers(auth["session_token"]),
    )
    assert patch.status_code == 200, patch.text
    return pid


async def _my_practices(client: AsyncClient, auth: dict) -> list[dict]:
    """Master's own practices (root + children of any published series)."""
    resp = await client.get(
        f"{MY_PRACTICES_URL}?limit=100",
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 200
    return resp.json()["items"]


def _by_id(items: list[dict], practice_id: str) -> dict:
    return next(i for i in items if i["id"] == practice_id)


def _children(items: list[dict], root_id: str) -> list[dict]:
    return [i for i in items if i.get("parent_practice_id") == root_id]


# ---------------------------------------------------------------------------
# recurrence_days mapping
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_series_card_daily_full_week(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """daily -> recurrence_days = the full week; total counts all occurrences.

    The same trio is reported by the root and by every child.
    """
    auth = await _make_verified_master(client, db_session)
    root_id = await _create_and_publish(
        client, auth,
        recurrence={"period": "daily", "end": "after_count", "count": 5},
    )

    items = await _my_practices(client, auth)
    root = _by_id(items, root_id)
    assert root["recurrence_days"] == [1, 2, 3, 4, 5, 6, 7]
    assert root["total_sessions"] == 5
    assert root["completed_sessions"] == 0

    for child in _children(items, root_id):
        assert child["recurrence_days"] == [1, 2, 3, 4, 5, 6, 7]
        assert child["total_sessions"] == 5
        assert child["completed_sessions"] == 0


@pytest.mark.asyncio
async def test_series_card_weekly_selected_days(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """weekly -> recurrence_days = the spec's chosen ISO weekdays (sorted)."""
    auth = await _make_verified_master(client, db_session)
    root_id = await _create_and_publish(
        client, auth,
        recurrence={
            "period": "weekly", "days": [5, 1, 3],
            "end": "after_count", "count": 4,
        },
    )

    root = _by_id(await _my_practices(client, auth), root_id)
    assert root["recurrence_days"] == [1, 3, 5]
    assert root["total_sessions"] == 4
    assert root["completed_sessions"] == 0


# ---------------------------------------------------------------------------
# Null meta for non-series / spec-less series
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_non_series_has_null_meta(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """A plain (non-series) practice carries no series meta."""
    auth = await _make_verified_master(client, db_session)
    pid = await _create_and_publish(client, auth)  # practice_type=live

    item = _by_id(await _my_practices(client, auth), pid)
    assert item["recurrence_days"] is None
    assert item["total_sessions"] is None
    assert item["completed_sessions"] is None


@pytest.mark.asyncio
async def test_series_without_spec_has_null_meta(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """A series TAG without a recurrence spec carries no meta (seed demo)."""
    auth = await _make_verified_master(client, db_session)
    pid = await _create_and_publish(
        client, auth, practice_type="series",  # no recurrence
    )

    item = _by_id(await _my_practices(client, auth), pid)
    assert item["recurrence_days"] is None
    assert item["total_sessions"] is None
    assert item["completed_sessions"] is None


# ---------------------------------------------------------------------------
# total excludes cancelled; completed counts status=completed
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_total_excludes_cancelled_completed_counted(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """A cancelled occurrence drops out of total; a completed one is counted.

    Start from 5 occurrences (root + 4 children); mark one child completed and
    another cancelled. total = 4 (5 minus the cancelled), completed = 1.
    """
    auth = await _make_verified_master(client, db_session)
    root_id = await _create_and_publish(
        client, auth,
        recurrence={"period": "daily", "end": "after_count", "count": 5},
    )

    kids = _children(await _my_practices(client, auth), root_id)
    assert len(kids) == 4

    await db_session.execute(
        update(Practice)
        .where(Practice.id == UUID(kids[0]["id"]))
        .values(status=PracticeStatus.COMPLETED.value)
    )
    await db_session.execute(
        update(Practice)
        .where(Practice.id == UUID(kids[1]["id"]))
        .values(status=PracticeStatus.CANCELLED.value)
    )
    await db_session.commit()

    root = _by_id(await _my_practices(client, auth), root_id)
    assert root["total_sessions"] == 4  # 5 minus the cancelled occurrence
    assert root["completed_sessions"] == 1


# ---------------------------------------------------------------------------
# Detail endpoint carries series meta (incl. when viewing a child)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_detail_endpoint_returns_series_meta(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """GET /practices/{id} surfaces series meta, including for a child occurrence."""
    auth = await _make_verified_master(client, db_session)
    root_id = await _create_and_publish(
        client, auth,
        recurrence={"period": "daily", "end": "after_count", "count": 4},
    )
    child_id = _children(await _my_practices(client, auth), root_id)[0]["id"]

    resp = await client.get(
        f"{PRACTICES_URL}/{child_id}",
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["recurrence_days"] == [1, 2, 3, 4, 5, 6, 7]
    assert body["total_sessions"] == 4
    assert body["completed_sessions"] == 0


# ---------------------------------------------------------------------------
# Public feed does NOT compute series meta
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_public_feed_omits_series_meta(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """The public feed leaves series meta None (it does not resolve it)."""
    auth = await _make_verified_master(client, db_session)
    master_id = auth["user"]["id"]
    await _create_and_publish(
        client, auth,
        recurrence={"period": "daily", "end": "after_count", "count": 3},
    )

    resp = await client.get(
        f"{PRACTICES_URL}?master_id={master_id}&limit=100",
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) >= 1  # root + children are future-scheduled
    for item in items:
        assert item["recurrence_days"] is None
        assert item["total_sessions"] is None
        assert item["completed_sessions"] is None


# ---------------------------------------------------------------------------
# No N+1: meta resolves in exactly two queries regardless of page size
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_series_meta_no_n_plus_one(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Resolving meta for several series on one page stays at two SELECTs."""
    auth = await _make_verified_master(client, db_session)
    master_id = auth["user"]["id"]
    for _ in range(3):  # three distinct series, each root + 2 children
        await _create_and_publish(
            client, auth,
            recurrence={"period": "daily", "end": "after_count", "count": 3},
        )

    from sqlalchemy import event, select
    from sqlalchemy.engine import Engine

    from app.core.database import get_session_factory
    from app.modules.practices.service import _series_meta_for_practices

    factory = get_session_factory()
    async with factory() as s:
        practices = list(
            (
                await s.execute(
                    select(Practice).where(
                        Practice.master_id == UUID(master_id)
                    )
                )
            ).scalars().all()
        )
        assert len(practices) == 9  # 3 series x (root + 2 children)

        selects: list[str] = []

        def _count(conn, cursor, statement, *args, **kwargs) -> None:
            if statement.lstrip().upper().startswith("SELECT"):
                selects.append(statement)

        event.listen(Engine, "before_cursor_execute", _count)
        try:
            meta = await _series_meta_for_practices(practices, s)
        finally:
            event.remove(Engine, "before_cursor_execute", _count)

    # Two queries (roots + grouped counts) for 9 practices across 3 series.
    assert len(selects) == 2, selects
    assert len(meta) == 9
    assert all(m[1] == 3 for m in meta.values())  # total_sessions == 3 each
