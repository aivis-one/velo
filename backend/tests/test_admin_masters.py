# =============================================================================
# Test: Admin -- Master verification and rejection (Phase 2.3)
# =============================================================================
#
# telegram_id ranges:
#   56001-56099 -- master applicants
#   56900-56999 -- admin users
# =============================================================================

from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.masters.models import MasterProfile
from app.modules.practices.taxonomy_models import TaxonomyDirection
from app.modules.users.models import User, UserRole
from tests.helpers import auth_headers, cleanup_range, login_user


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
VERIFY_URL = "/api/v1/admin/masters/{user_id}/verify"
REJECT_URL = "/api/v1/admin/masters/{user_id}/reject"
METHODS_URL = "/api/v1/admin/masters/{user_id}/methods"
PROFILE_URL = "/api/v1/admin/masters/{user_id}/profile"
DETAIL_URL = "/api/v1/admin/masters/{user_id}"
APPLY_URL = "/api/v1/masters/apply"

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
async def cleanup(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    """Clean master_profiles and reset roles for test range before/after."""
    await cleanup_range(db_session, 56000, 56999)
    await db_session.commit()
    yield
    await cleanup_range(db_session, 56000, 56999)
    # ПРОМТ №503 commit 3: verify's new promote param can insert custom
    # TaxonomyDirection rows (same "custom_" value prefix as
    # _promote_custom_methods' other caller, approve_method_change -- see
    # test_master_method_change.py's identical cleanup) -- clean those up too.
    await db_session.execute(
        delete(TaxonomyDirection).where(TaxonomyDirection.value.like("custom_%"))
    )
    await db_session.commit()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _valid_apply_body(methods: list[str] | None = None) -> dict:
    """Minimal valid master application payload."""
    return {
        "profile": {
            "display_name": "Verify Test Master",
            "email": "verify@test.com",
            "phone": "+1234567890",
        },
        "experience": {
            "methods": methods or ["meditation"],
            "experience_years": 5,
            "bio": "Test master for admin verification",
            "certifications": ["Cert A"],
        },
        "documents": [{"type": "certificate", "number": "CERT-001"}],
    }


async def _create_applicant(
    client: AsyncClient,
    telegram_id: int,
    first_name: str = "Applicant",
    methods: list[str] | None = None,
) -> tuple[dict, str]:
    """Create a user and submit a master application. Returns (auth_data, token)."""
    auth = await login_user(
        client, telegram_id=telegram_id, first_name=first_name
    )
    token = auth["session_token"]

    resp = await client.post(
        APPLY_URL,
        json=_valid_apply_body(methods=methods),
        headers=auth_headers(token),
    )
    assert resp.status_code == 201
    return auth, token


async def _make_admin(
    client: AsyncClient,
    db_session: AsyncSession,
    telegram_id: int = 56900,
    first_name: str = "Admin",
) -> tuple[dict, str]:
    """Create a user and upgrade to admin role. Returns (auth_data, token)."""
    auth = await login_user(
        client, telegram_id=telegram_id, first_name=first_name
    )
    token = auth["session_token"]
    user_id = auth["user"]["id"]

    await db_session.execute(
        update(User)
        .where(User.id == user_id)
        .values(role=UserRole.ADMIN.value)
    )
    await db_session.commit()

    return auth, token


# ---------------------------------------------------------------------------
# POST /admin/masters/{user_id}/verify -- success
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_verify_master_success(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Admin verifies pending application: status=verified, role=master."""
    # Setup: applicant + admin.
    applicant_auth, _ = await _create_applicant(client, telegram_id=56001)
    _, admin_token = await _make_admin(client, db_session)

    user_id = applicant_auth["user"]["id"]
    url = VERIFY_URL.format(user_id=user_id)

    # Act.
    resp = await client.post(
        url,
        json={"notes": "All documents OK"},
        headers=auth_headers(admin_token),
    )

    # Assert response.
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "verified"
    assert data["user_id"] == user_id

    # Assert DB: profile status.
    profile = await db_session.get(MasterProfile, user_id)
    await db_session.refresh(profile)
    assert profile.data["account"]["status"] == "verified"
    assert profile.data["account"]["verification"]["notes"] == "All documents OK"

    # Assert DB: role UNCHANGED (T4 — approval grants capability, not role; the
    # user self-switches to master via POST /users/me/role afterwards).
    user = await db_session.get(User, user_id)
    await db_session.refresh(user)
    assert user.role == UserRole.USER


# ---------------------------------------------------------------------------
# POST /admin/masters/{user_id}/verify -- no notes (optional)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_verify_master_no_notes(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Verify without notes: success, notes=null in JSONB."""
    applicant_auth, _ = await _create_applicant(client, telegram_id=56002)
    _, admin_token = await _make_admin(client, db_session, telegram_id=56901)

    user_id = applicant_auth["user"]["id"]
    url = VERIFY_URL.format(user_id=user_id)

    resp = await client.post(
        url,
        json={},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 200

    profile = await db_session.get(MasterProfile, user_id)
    await db_session.refresh(profile)
    assert profile.data["account"]["verification"]["notes"] is None


# ---------------------------------------------------------------------------
# POST /admin/masters/{user_id}/verify -- promote (ПРОМТ №503 commit 3)
#
# Before this, ONLY an already-verified master's later method-change request
# (approve_method_change) could promote a custom label into the taxonomy
# catalog -- a brand-new applicant's «Свой вариант» text had NO promotion
# path at all, no matter what the admin did on verify. These three mirror
# test_master_method_change.py's approve+promote trio exactly, against the
# initial-application endpoint instead.
#
# ПРОМТ №507 POSTMORTEM (deploy gate, first-ever run of these three tests):
# test_verify_with_promote_creates_custom_direction originally used
# "Дыхательные практики" as its "creates a NEW row" fixture -- that label is
# a REAL SEEDED direction (source='seed', migration 1a2b3c4d5e6f, value=
# 'breathwork'), not an absent one. _promote_custom_methods correctly
# deduped it (nothing to promote -- `promoted_to_catalog=[]` in the deploy
# log), and the assertion then queried the PRE-EXISTING seed row and
# expected its source to be 'custom' -- `assert 'seed' == 'custom'`. A test
# defect, not a product defect: confirmed independently via (a) the
# migration's own source, which sets source='seed' on every row in
# _DIRECTIONS including ("breathwork", "Дыхательные практики"), and (b) the
# SAME deploy run's test_master_method_change.py::
# test_approve_with_promote_creates_custom_direction, exercising the exact
# same _promote_custom_methods helper via its OTHER caller
# (approve_method_change) with a genuinely novel label ("Ченнелинг", absent
# from every migration/seed file) -- that test PASSED, proving the shared
# promotion mechanism itself works in this deploy DB. What that sibling
# test does NOT prove is that THIS code's new addition -- verify_master's
# promote parameter, wired in ПРОМТ №503 commit 3 -- threads the value
# through correctly on its OWN path; only a passing run of the fixed test
# below (obviously-synthetic label, not a mere "absent today" one) proves
# that specifically, and it is unproven until the next deploy.
# ---------------------------------------------------------------------------

# Deliberately synthetic -- not a plausible real practice-direction name a
# future seed migration could ever add by coincidence (the whole failure
# above was a real seed colliding with a "must not already exist" fixture).
# Referencing this prompt number in the label itself is the guard: no
# legitimate content curator chooses a string like this.
_NOVEL_CUSTOM_LABEL = "Синтетическое направление ПРОМТ-507 (не реальная практика)"
_NOVEL_DEDUP_COMPANION_LABEL = "Синтетический компаньон-дедуп ПРОМТ-507"


@pytest.mark.asyncio
async def test_verify_without_promote_leaves_catalog_unchanged(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """A verify body with no promote (every caller before this field existed)
    writes nothing to the taxonomy catalog."""
    before = (await db_session.execute(select(TaxonomyDirection.id))).scalars().all()

    applicant_auth, _ = await _create_applicant(
        client, telegram_id=56060, methods=["Дыхательные практики"]
    )
    _, admin_token = await _make_admin(client, db_session, telegram_id=56960)
    user_id = applicant_auth["user"]["id"]

    resp = await client.post(
        VERIFY_URL.format(user_id=user_id),
        json={"notes": "OK"},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 200

    after = (await db_session.execute(select(TaxonomyDirection.id))).scalars().all()
    assert set(after) == set(before)


@pytest.mark.asyncio
async def test_verify_with_promote_creates_custom_direction(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """promote=[label] on the INITIAL application's verify inserts a new
    source='custom' direction -- the previously-missing promotion path for a
    brand-new applicant. Does NOT rewrite the applicant's own stored methods
    text -- only the catalog gains the row; the frontend resolves the
    existing text to the new chip via label matching (ПРОМТ №503 commits 1-2).

    Asserts its own premise first (ПРОМТ №507): if this label somehow
    already existed, a future failure here names that cause directly
    instead of surfacing as a confusing 'seed' == 'custom' mismatch three
    assertions later, the way the ПРОМТ №507 deploy failure did.
    """
    premise = (
        await db_session.execute(
            select(TaxonomyDirection.id).where(
                TaxonomyDirection.label == _NOVEL_CUSTOM_LABEL
            )
        )
    ).scalars().all()
    assert premise == [], (
        f"premise violated: {_NOVEL_CUSTOM_LABEL!r} already exists in the "
        "catalog -- this test needs a label that is genuinely absent"
    )

    applicant_auth, _ = await _create_applicant(
        client, telegram_id=56061, methods=[_NOVEL_CUSTOM_LABEL]
    )
    _, admin_token = await _make_admin(client, db_session, telegram_id=56961)
    user_id = applicant_auth["user"]["id"]

    resp = await client.post(
        VERIFY_URL.format(user_id=user_id),
        json={"promote": [_NOVEL_CUSTOM_LABEL]},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "verified"

    profile = await db_session.get(MasterProfile, user_id)
    await db_session.refresh(profile)
    assert profile.data["profile"]["methods"] == [_NOVEL_CUSTOM_LABEL]

    row = (
        await db_session.execute(
            select(TaxonomyDirection).where(
                TaxonomyDirection.label == _NOVEL_CUSTOM_LABEL
            )
        )
    ).scalar_one()
    assert row.source == "custom"
    assert row.is_active is True
    assert row.value.startswith("custom_")


@pytest.mark.asyncio
async def test_verify_with_promote_dedups_existing_label(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Promoting a label that already exists in the catalog (seeded) does
    not create a duplicate row.

    ПРОМТ №507: an earlier version of this test submitted ONLY the existing
    label and asserted the row count stayed at 1 -- which cannot tell
    "dedup correctly skipped it" apart from "promote never reached the
    service at all" (both leave the count at 1; nothing here proves the
    code path was even exercised). A companion genuinely-novel label in the
    SAME promote call closes that gap: it can only end up in the catalog if
    promote genuinely reached _promote_custom_methods and the loop
    processed every entry, not merely short-circuited on an empty list.
    """
    existing = (
        await db_session.execute(
            select(TaxonomyDirection.id).where(TaxonomyDirection.label == "Медитация")
        )
    ).scalars().all()
    assert len(existing) == 1  # the R5-seeded "meditation" direction

    companion_premise = (
        await db_session.execute(
            select(TaxonomyDirection.id).where(
                TaxonomyDirection.label == _NOVEL_DEDUP_COMPANION_LABEL
            )
        )
    ).scalars().all()
    assert companion_premise == [], (
        f"premise violated: {_NOVEL_DEDUP_COMPANION_LABEL!r} already exists"
    )

    applicant_auth, _ = await _create_applicant(
        client,
        telegram_id=56062,
        methods=["Медитация", _NOVEL_DEDUP_COMPANION_LABEL],
    )
    _, admin_token = await _make_admin(client, db_session, telegram_id=56962)
    user_id = applicant_auth["user"]["id"]

    resp = await client.post(
        VERIFY_URL.format(user_id=user_id),
        json={"promote": ["Медитация", _NOVEL_DEDUP_COMPANION_LABEL]},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 200

    after = (
        await db_session.execute(
            select(TaxonomyDirection.id).where(TaxonomyDirection.label == "Медитация")
        )
    ).scalars().all()
    assert len(after) == 1  # still just the one seeded row -- no dup

    # Proves promote genuinely reached the service on THIS test's own
    # evidence, not borrowed from a sibling: the companion must now exist.
    companion_row = (
        await db_session.execute(
            select(TaxonomyDirection).where(
                TaxonomyDirection.label == _NOVEL_DEDUP_COMPANION_LABEL
            )
        )
    ).scalar_one()
    assert companion_row.source == "custom"
    assert companion_row.value.startswith("custom_")


# ---------------------------------------------------------------------------
# POST /admin/masters/{user_id}/reject -- success
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_reject_master_success(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Admin rejects pending application: status=rejected, role stays USER."""
    applicant_auth, _ = await _create_applicant(client, telegram_id=56003)
    _, admin_token = await _make_admin(client, db_session, telegram_id=56902)

    user_id = applicant_auth["user"]["id"]
    url = REJECT_URL.format(user_id=user_id)

    resp = await client.post(
        url,
        json={"reason": "Insufficient experience"},
        headers=auth_headers(admin_token),
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "rejected"
    assert data["user_id"] == user_id

    # Assert DB: profile status.
    profile = await db_session.get(MasterProfile, user_id)
    await db_session.refresh(profile)
    assert profile.data["account"]["status"] == "rejected"
    assert profile.data["account"]["rejection_reason"] == "Insufficient experience"

    # Assert DB: user role NOT changed.
    user = await db_session.get(User, user_id)
    await db_session.refresh(user)
    assert user.role == UserRole.USER


# ---------------------------------------------------------------------------
# POST /admin/masters/{user_id}/verify -- no auth
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_verify_no_auth(client: AsyncClient) -> None:
    """No Authorization header: 401."""
    url = VERIFY_URL.format(user_id=uuid4())
    resp = await client.post(url, json={})
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# POST /admin/masters/{user_id}/verify -- non-admin
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_verify_non_admin(client: AsyncClient) -> None:
    """Regular user (not admin): 403."""
    auth = await login_user(client, telegram_id=56010, first_name="NotAdmin")
    url = VERIFY_URL.format(user_id=uuid4())

    resp = await client.post(
        url,
        json={},
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# POST /admin/masters/{user_id}/verify -- not found
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_verify_nonexistent_user(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Non-existent user_id: 404."""
    _, admin_token = await _make_admin(client, db_session, telegram_id=56903)

    url = VERIFY_URL.format(user_id=uuid4())
    resp = await client.post(
        url,
        json={},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# POST /admin/masters/{user_id}/verify -- already verified
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_verify_already_verified(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Verifying an already-verified master: 409."""
    applicant_auth, _ = await _create_applicant(client, telegram_id=56004)
    _, admin_token = await _make_admin(client, db_session, telegram_id=56904)

    user_id = applicant_auth["user"]["id"]
    url = VERIFY_URL.format(user_id=user_id)

    # First verify -- success.
    resp1 = await client.post(url, json={}, headers=auth_headers(admin_token))
    assert resp1.status_code == 200

    # Second verify -- conflict.
    resp2 = await client.post(url, json={}, headers=auth_headers(admin_token))
    assert resp2.status_code == 409


# ---------------------------------------------------------------------------
# POST /admin/masters/{user_id}/verify -- rejected profile
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_verify_rejected_profile(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Cannot verify a rejected application (must reapply first): 409."""
    applicant_auth, _ = await _create_applicant(client, telegram_id=56005)
    _, admin_token = await _make_admin(client, db_session, telegram_id=56905)

    user_id = applicant_auth["user"]["id"]

    # Reject first.
    reject_url = REJECT_URL.format(user_id=user_id)
    resp1 = await client.post(
        reject_url,
        json={"reason": "Not ready"},
        headers=auth_headers(admin_token),
    )
    assert resp1.status_code == 200

    # Try to verify the rejected profile.
    verify_url = VERIFY_URL.format(user_id=user_id)
    resp2 = await client.post(
        verify_url, json={}, headers=auth_headers(admin_token)
    )
    assert resp2.status_code == 409


# ---------------------------------------------------------------------------
# POST /admin/masters/{user_id}/reject -- empty reason
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_reject_empty_reason(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Rejection without reason: 422 validation error."""
    _, admin_token = await _make_admin(client, db_session, telegram_id=56906)

    url = REJECT_URL.format(user_id=uuid4())
    resp = await client.post(
        url,
        json={"reason": ""},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Integration: reject -> reapply -> verify (full cycle)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_reject_reapply_verify_cycle(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Full lifecycle: apply -> reject -> reapply -> verify."""
    applicant_auth, applicant_token = await _create_applicant(
        client, telegram_id=56006
    )
    _, admin_token = await _make_admin(client, db_session, telegram_id=56907)
    user_id = applicant_auth["user"]["id"]

    # Step 1: Admin rejects.
    reject_url = REJECT_URL.format(user_id=user_id)
    resp1 = await client.post(
        reject_url,
        json={"reason": "Need more experience"},
        headers=auth_headers(admin_token),
    )
    assert resp1.status_code == 200

    # Step 2: User reapplies.
    new_body = _valid_apply_body()
    new_body["experience"]["experience_years"] = 10
    resp2 = await client.post(
        APPLY_URL,
        json=new_body,
        headers=auth_headers(applicant_token),
    )
    assert resp2.status_code == 201
    assert resp2.json()["status"] == "pending"

    # Step 3: Admin verifies.
    verify_url = VERIFY_URL.format(user_id=user_id)
    resp3 = await client.post(
        verify_url,
        json={"notes": "Improved application"},
        headers=auth_headers(admin_token),
    )
    assert resp3.status_code == 200
    assert resp3.json()["status"] == "verified"

    # Assert: rejection history preserved.
    profile = await db_session.get(MasterProfile, user_id)
    await db_session.refresh(profile)
    rejections = profile.data["account"].get("rejections", [])
    assert len(rejections) == 1
    assert rejections[0]["reason"] == "Need more experience"

    # Assert: role UNCHANGED after re-verify (T4 — capability, not role flip).
    user = await db_session.get(User, user_id)
    await db_session.refresh(user)
    assert user.role == UserRole.USER


# ---------------------------------------------------------------------------
# GET /admin/masters/{user_id} -- detail carries methods/experience/bio (T3)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_master_detail_carries_profile_fields(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """The detail endpoint returns real methods / experience_years / bio."""
    applicant_auth, _ = await _create_applicant(client, telegram_id=56040)
    _, admin_token = await _make_admin(client, db_session)
    user_id = applicant_auth["user"]["id"]

    resp = await client.get(
        DETAIL_URL.format(user_id=user_id), headers=auth_headers(admin_token)
    )
    assert resp.status_code == 200
    data = resp.json()
    # _valid_apply_body seeds methods=["meditation"], experience_years=5.
    assert data["methods"] == ["meditation"]
    assert data["experience_years"] == 5
    assert data["bio"] == "Test master for admin verification"


# ---------------------------------------------------------------------------
# PATCH /admin/masters/{user_id}/methods (T3)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_edit_methods_success(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Admin overwrites the master's methods; detail reflects the new set."""
    applicant_auth, _ = await _create_applicant(client, telegram_id=56041)
    _, admin_token = await _make_admin(client, db_session)
    user_id = applicant_auth["user"]["id"]

    resp = await client.patch(
        METHODS_URL.format(user_id=user_id),
        json={"methods": ["yoga", "tantra"]},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 200
    assert resp.json()["user_id"] == user_id

    # DB reflects the new flat method list.
    profile = await db_session.get(MasterProfile, user_id)
    await db_session.refresh(profile)
    assert profile.data["profile"]["methods"] == ["yoga", "tantra"]

    # Detail endpoint returns the updated methods.
    detail = await client.get(
        DETAIL_URL.format(user_id=user_id), headers=auth_headers(admin_token)
    )
    assert detail.json()["methods"] == ["yoga", "tantra"]


@pytest.mark.asyncio
async def test_edit_methods_empty_rejected(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Empty method list is a 422 (min 1, mirrors the apply rule)."""
    applicant_auth, _ = await _create_applicant(client, telegram_id=56042)
    _, admin_token = await _make_admin(client, db_session)
    user_id = applicant_auth["user"]["id"]

    resp = await client.patch(
        METHODS_URL.format(user_id=user_id),
        json={"methods": []},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_edit_methods_not_found(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Editing methods for a non-master user_id is a 404."""
    _, admin_token = await _make_admin(client, db_session)
    resp = await client.patch(
        METHODS_URL.format(user_id=uuid4()),
        json={"methods": ["yoga"]},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_edit_methods_non_admin(client: AsyncClient) -> None:
    """A non-admin caller is forbidden."""
    auth = await login_user(client, telegram_id=56043, first_name="NotAdmin")
    resp = await client.patch(
        METHODS_URL.format(user_id=auth["user"]["id"]),
        json={"methods": ["yoga"]},
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# GET /admin/masters/{user_id} -- detail carries ALL editable fields (batch H)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_master_detail_carries_all_editable_fields(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """The detail endpoint returns email / phone / languages / certifications."""
    applicant_auth, _ = await _create_applicant(client, telegram_id=56050)
    _, admin_token = await _make_admin(client, db_session)
    user_id = applicant_auth["user"]["id"]

    resp = await client.get(
        DETAIL_URL.format(user_id=user_id), headers=auth_headers(admin_token)
    )
    assert resp.status_code == 200
    data = resp.json()
    # _valid_apply_body seeds display_name/email/phone/certifications; languages [].
    assert data["display_name"] == "Verify Test Master"
    assert data["email"] == "verify@test.com"
    assert data["phone"] == "+1234567890"
    assert data["certifications"] == ["Cert A"]
    assert data["languages"] == []


# ---------------------------------------------------------------------------
# PATCH /admin/masters/{user_id}/profile (batch H)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_edit_profile_partial_update_preserves_siblings(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """A partial PATCH writes only the sent keys; unsent siblings survive."""
    applicant_auth, _ = await _create_applicant(client, telegram_id=56051)
    _, admin_token = await _make_admin(client, db_session)
    user_id = applicant_auth["user"]["id"]

    resp = await client.patch(
        PROFILE_URL.format(user_id=user_id),
        json={"display_name": "New Name", "bio": "Rewritten bio"},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 200
    assert resp.json()["user_id"] == user_id

    profile = await db_session.get(MasterProfile, user_id)
    await db_session.refresh(profile)
    prof = profile.data["profile"]
    # Sent keys applied.
    assert prof["display_name"] == "New Name"
    assert prof["bio"] == "Rewritten bio"
    # Unsent siblings untouched (methods/experience/email/phone/certifications).
    assert prof["methods"] == ["meditation"]
    assert prof["experience_years"] == 5
    assert prof["email"] == "verify@test.com"
    assert prof["phone"] == "+1234567890"
    assert prof["certifications"] == ["Cert A"]
    # account block (status) never touched by a profile edit.
    assert profile.data["account"]["status"] == "pending"


@pytest.mark.asyncio
async def test_edit_profile_all_fields(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Every editable data.profile.* field can be written in one call."""
    applicant_auth, _ = await _create_applicant(client, telegram_id=56052)
    _, admin_token = await _make_admin(client, db_session)
    user_id = applicant_auth["user"]["id"]

    resp = await client.patch(
        PROFILE_URL.format(user_id=user_id),
        json={
            "display_name": "Full Edit",
            "email": "new@test.com",
            "phone": "+79990001122",
            "bio": "Full bio",
            "methods": ["yoga", "breathwork"],
            "experience_years": 12,
            "certifications": ["Cert X", "Cert Y"],
            "languages": ["Русский", "English"],
        },
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 200

    profile = await db_session.get(MasterProfile, user_id)
    await db_session.refresh(profile)
    prof = profile.data["profile"]
    assert prof["display_name"] == "Full Edit"
    assert prof["email"] == "new@test.com"
    assert prof["phone"] == "+79990001122"
    assert prof["bio"] == "Full bio"
    assert prof["methods"] == ["yoga", "breathwork"]
    assert prof["experience_years"] == 12
    assert prof["certifications"] == ["Cert X", "Cert Y"]
    assert prof["languages"] == ["Русский", "English"]


@pytest.mark.asyncio
async def test_edit_profile_updates_account_name(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """first_name / last_name write to the User row (В1=В both names)."""
    applicant_auth, _ = await _create_applicant(client, telegram_id=56053)
    _, admin_token = await _make_admin(client, db_session)
    user_id = applicant_auth["user"]["id"]

    resp = await client.patch(
        PROFILE_URL.format(user_id=user_id),
        json={"first_name": "Ivan", "last_name": "Petrov"},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 200

    user = await db_session.get(User, user_id)
    await db_session.refresh(user)
    assert user.first_name == "Ivan"
    assert user.last_name == "Petrov"

    # Detail (admin list name) reflects the updated account name.
    detail = await client.get(
        DETAIL_URL.format(user_id=user_id), headers=auth_headers(admin_token)
    )
    assert detail.json()["first_name"] == "Ivan"
    assert detail.json()["last_name"] == "Petrov"


@pytest.mark.asyncio
async def test_edit_profile_works_on_verified_master(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """The edit works post-verification (ANY status, no gate)."""
    applicant_auth, _ = await _create_applicant(client, telegram_id=56054)
    _, admin_token = await _make_admin(client, db_session)
    user_id = applicant_auth["user"]["id"]

    # Verify first -> status=verified.
    verify = await client.post(
        VERIFY_URL.format(user_id=user_id),
        json={"notes": "ok"},
        headers=auth_headers(admin_token),
    )
    assert verify.json()["status"] == "verified"

    # Now edit the verified master's profile.
    resp = await client.patch(
        PROFILE_URL.format(user_id=user_id),
        json={"bio": "Edited after verification"},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 200

    profile = await db_session.get(MasterProfile, user_id)
    await db_session.refresh(profile)
    assert profile.data["profile"]["bio"] == "Edited after verification"
    # Status stays verified -- a profile edit never changes account status.
    assert profile.data["account"]["status"] == "verified"


@pytest.mark.asyncio
async def test_edit_profile_validation_rejects(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Bad email / out-of-range experience / over-long name are 422."""
    applicant_auth, _ = await _create_applicant(client, telegram_id=56055)
    _, admin_token = await _make_admin(client, db_session)
    user_id = applicant_auth["user"]["id"]
    url = PROFILE_URL.format(user_id=user_id)
    headers = auth_headers(admin_token)

    assert (
        await client.patch(url, json={"email": "not-an-email"}, headers=headers)
    ).status_code == 422
    assert (
        await client.patch(url, json={"experience_years": 99}, headers=headers)
    ).status_code == 422
    assert (
        await client.patch(url, json={"display_name": "x" * 101}, headers=headers)
    ).status_code == 422
    # methods, if provided, still obeys the >=1 apply rule.
    assert (
        await client.patch(url, json={"methods": []}, headers=headers)
    ).status_code == 422


@pytest.mark.asyncio
async def test_edit_profile_not_found(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Editing a non-master user_id is a 404."""
    _, admin_token = await _make_admin(client, db_session)
    resp = await client.patch(
        PROFILE_URL.format(user_id=uuid4()),
        json={"bio": "x"},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_edit_profile_non_admin(client: AsyncClient) -> None:
    """A non-admin caller is forbidden."""
    auth = await login_user(client, telegram_id=56056, first_name="NotAdmin")
    resp = await client.patch(
        PROFILE_URL.format(user_id=auth["user"]["id"]),
        json={"bio": "x"},
        headers=auth_headers(auth["session_token"]),
    )
    assert resp.status_code == 403
