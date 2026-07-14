# =============================================================================
# Test: Taxonomy -- authenticated active-catalog read (R5 stage 3a)
# =============================================================================
#
# GET /api/v1/taxonomy -- any authenticated user (not admin-gated), active
# rows only. Distinct from GET /api/v1/admin/taxonomy (admin-only, incl.
# inactive), covered in test_admin_taxonomy.py.
#
# telegram_id range: 58970-58989. Test-created directions/styles are
# prefixed "zz_test_" and cleaned up before/after each test.
# =============================================================================

from collections.abc import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.practices.taxonomy_models import TaxonomyDirection, TaxonomyStyle
from app.modules.users.models import User, UserRole
from tests.helpers import auth_headers, full_cleanup_range, login_user

TAXONOMY_URL = "/api/v1/taxonomy"
ADMIN_DIRECTIONS_URL = "/api/v1/admin/taxonomy/directions"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
async def cleanup(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    await _do_cleanup(db_session)
    yield
    await _do_cleanup(db_session)


async def _do_cleanup(session: AsyncSession) -> None:
    # full_cleanup_range rolls back first (TD-032) -- must run before our own
    # deletes below (see test_admin_taxonomy.py for the same ordering note).
    await full_cleanup_range(session, 58970, 58989, delete_users=False)
    await session.execute(
        delete(TaxonomyStyle).where(TaxonomyStyle.value.like("zz_test_%"))
    )
    await session.execute(
        delete(TaxonomyDirection).where(TaxonomyDirection.value.like("zz_test_%"))
    )
    await session.commit()


async def _make_admin(
    client: AsyncClient,
    db_session: AsyncSession,
    telegram_id: int,
) -> str:
    auth = await login_user(client, telegram_id=telegram_id, first_name="TaxAdmin")
    await db_session.execute(
        update(User)
        .where(User.id == auth["user"]["id"])
        .values(role=UserRole.ADMIN.value)
    )
    await db_session.commit()
    return auth["session_token"]


# ---------------------------------------------------------------------------
# GET /api/v1/taxonomy -- auth + seed content
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_active_taxonomy_no_auth(client: AsyncClient) -> None:
    resp = await client.get(TAXONOMY_URL)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_active_taxonomy_any_authenticated_role(client: AsyncClient) -> None:
    """A plain (non-admin, non-master) user can read the active catalog."""
    auth = await login_user(client, telegram_id=58970, first_name="PlainUser")
    resp = await client.get(
        TAXONOMY_URL, headers=auth_headers(auth["session_token"])
    )
    assert resp.status_code == 200
    data = resp.json()

    directions = {d["value"]: d for d in data["directions"]}
    assert "yoga" in directions
    yoga_styles = {s["value"] for s in directions["yoga"]["styles"]}
    assert yoga_styles == {"nidra", "yin", "hatha", "vinyasa", "kundalini", "ashtanga"}
    # A direction with no styles has an empty list.
    assert directions["breathwork"]["styles"] == []
    # Every returned row is active (this endpoint is active-only by contract).
    for d in data["directions"]:
        assert d["is_active"] is True
        for s in d["styles"]:
            assert s["is_active"] is True


@pytest.mark.asyncio
async def test_active_taxonomy_excludes_inactive_direction(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    admin_token = await _make_admin(client, db_session, telegram_id=58971)

    create_resp = await client.post(
        ADMIN_DIRECTIONS_URL,
        json={"value": "zz_test_activedir", "label": "Active Dir Test"},
        headers=auth_headers(admin_token),
    )
    direction_id = create_resp.json()["id"]

    # Active by default -- present on the public endpoint.
    before = await client.get(TAXONOMY_URL, headers=auth_headers(admin_token))
    assert "zz_test_activedir" in {d["value"] for d in before.json()["directions"]}

    # Deactivate via the admin API -- must disappear from the public list.
    await client.patch(
        f"{ADMIN_DIRECTIONS_URL}/{direction_id}",
        json={"is_active": False},
        headers=auth_headers(admin_token),
    )
    after = await client.get(TAXONOMY_URL, headers=auth_headers(admin_token))
    assert "zz_test_activedir" not in {d["value"] for d in after.json()["directions"]}


@pytest.mark.asyncio
async def test_active_taxonomy_excludes_inactive_style_keeps_direction(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Deactivating one style under a seeded direction drops only that style
    -- the direction and its other (still-active) seeded styles remain."""
    admin_token = await _make_admin(client, db_session, telegram_id=58972)

    # "yoga" is a real seeded direction (migration) -- fetch its id.
    list_resp = await client.get(
        "/api/v1/admin/taxonomy", headers=auth_headers(admin_token)
    )
    yoga_id = next(
        d["id"] for d in list_resp.json()["directions"] if d["value"] == "yoga"
    )

    style_resp = await client.post(
        f"{ADMIN_DIRECTIONS_URL}/{yoga_id}/styles",
        json={"value": "zz_test_activestyle", "label": "Active Style Test"},
        headers=auth_headers(admin_token),
    )
    style_id = style_resp.json()["id"]

    await client.patch(
        f"/api/v1/admin/taxonomy/styles/{style_id}",
        json={"is_active": False},
        headers=auth_headers(admin_token),
    )

    resp = await client.get(TAXONOMY_URL, headers=auth_headers(admin_token))
    directions = {d["value"]: d for d in resp.json()["directions"]}
    assert "yoga" in directions  # direction itself untouched
    yoga_style_values = {s["value"] for s in directions["yoga"]["styles"]}
    assert "zz_test_activestyle" not in yoga_style_values  # deactivated style dropped
    assert "hatha" in yoga_style_values  # seeded active styles untouched
