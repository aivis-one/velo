# =============================================================================
# Test: Master public profile (S-4) + master_avatar_url in practice detail
# =============================================================================
#
# Covers GET /api/v1/masters/{user_id} (MasterPublicResponse) and the
# master_avatar_url field surfaced on GET /api/v1/practices/{id}.
#
# telegram_id ranges (56500-56599 -- this module owns this sub-range):
#   56501        -- verified master (default in _make_verified_master)
#   56510-56551  -- viewers / reviewers / applicants (non-master)
#   56590        -- admin (ADMIN_TID)
#
# NOTE: moved out of the shared 56xxx block to 56500-56599 to avoid colliding
# with test_admin_masters.py (56001-56010 applicants, 56900-56907 admins),
# which also cleans the whole 56000-56999 range. Both modules used to share
# 56xxx and only stayed green because cleanup ran between modules -- fragile.
# Now this module lives in and cleans ONLY 56500-56599 (TD-TGID-56XXX closed).
#
# Counters and avatar are exercised with direct ORM writes (Practice,
# Feedback, User.avatar_url) -- we do not drive the full booking ->
# attend -> completed -> feedback flow here; the aggregate queries only
# care about the rows existing.
# =============================================================================

from collections.abc import AsyncGenerator
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.bookings.models import Booking, BookingStatus
from app.modules.diary.models import Feedback
from app.modules.practices.models import Practice, PracticeStatus
from app.modules.users.models import User, UserRole
from tests.helpers import auth_headers, login_user, full_cleanup_range, switch_self_to_master

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MASTERS_URL = "/api/v1/masters"
PRACTICES_URL = "/api/v1/practices"
APPLY_URL = "/api/v1/masters/apply"
VERIFY_URL = "/api/v1/admin/masters/{user_id}/verify"

ADMIN_TID = 56590


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
    """Full ORM cleanup for telegram_id 56500-56599."""
    await full_cleanup_range(session, 56500, 56599, delete_users=False)
    await session.commit()


def _valid_apply_body() -> dict:
    """Return a valid MasterApplyRequest body."""
    return {
        "profile": {
            "display_name": "Alex Mindful",
            "email": "alex@test.com",
            "phone": "+1234567890",
        },
        "experience": {
            "methods": ["meditation", "mindfulness"],
            "experience_years": 10,
            "bio": "10 years of meditation practice.",
            "certifications": ["MBSR"],
        },
        "documents": [],
    }


async def _make_verified_master(
    client: AsyncClient,
    db_session: AsyncSession,
    telegram_id: int = 56501,
) -> dict:
    """Create user, apply as master, verify via admin. Returns master auth.

    Mirrors the helper in test_practices.py but scoped to the 56xxx range.
    """
    auth = await login_user(
        client, telegram_id=telegram_id, first_name="Master",
    )
    await client.post(
        APPLY_URL,
        json=_valid_apply_body(),
        headers=auth_headers(auth["session_token"]),
    )

    # Promote admin user and re-login to pick up the role.
    await login_user(client, telegram_id=ADMIN_TID, first_name="Admin")
    await db_session.execute(
        update(User)
        .where(User.telegram_id == ADMIN_TID)
        .values(role=UserRole.ADMIN.value)
    )
    await db_session.commit()
    admin_auth = await login_user(
        client, telegram_id=ADMIN_TID, first_name="Admin",
    )

    user_id = auth["user"]["id"]
    verify_resp = await client.post(
        VERIFY_URL.format(user_id=user_id),
        json={},
        headers=auth_headers(admin_auth["session_token"]),
    )
    assert verify_resp.status_code == 200

    # Re-login to pick up master role in session.
    await switch_self_to_master(client, auth["session_token"])
    return await login_user(
        client, telegram_id=telegram_id, first_name="Master",
    )


async def _insert_practice(
    session: AsyncSession,
    master_id: UUID,
    *,
    status: str = PracticeStatus.SCHEDULED.value,
) -> Practice:
    """Insert a Practice row directly via ORM (bypasses CRUD flow).

    set_jsonb is used for the JSONB data sandbox so SQLAlchemy emits the
    write (JSONBMixin convention). taxonomy is included for realism.
    """
    practice = Practice(
        master_id=master_id,
        practice_type="live",
        title="Morning Meditation",
        description="Guided session",
        scheduled_at=datetime.now(timezone.utc) + timedelta(days=7),
        duration_minutes=45,
        timezone="Europe/Moscow",
        max_participants=20,
        is_free=False,
        price_cents=150000,
        currency="eur",
        status=status,
    )
    practice.set_jsonb(
        "data",
        {
            "taxonomy": {
                "direction": "meditation",
                "difficulty": "medium",
                "style": None,
            },
        },
    )
    session.add(practice)
    await session.flush()
    return practice


async def _insert_feedback(
    session: AsyncSession,
    practice_id: UUID,
    user_id: UUID,
    *,
    rating: int = 9,
) -> None:
    """Insert a Booking + Feedback row directly via ORM.

    Feedback.booking_id is a NOT NULL FK -> bookings.id, and the test
    suite runs against real PostgreSQL, so the FK is enforced: we must
    create a genuine Booking first rather than fabricate a UUID. The
    reviews_count aggregate joins Feedback -> Practice and never reads
    booking_id; the Booking just satisfies the constraint. Both rows are
    removed by full_cleanup_range at teardown in FK-safe order.
    """
    booking = Booking(
        practice_id=practice_id,
        user_id=user_id,
        status=BookingStatus.ATTENDED.value,
    )
    session.add(booking)
    await session.flush()

    feedback = Feedback(
        practice_id=practice_id,
        user_id=user_id,
        booking_id=booking.id,
        rating=rating,
    )
    session.add(feedback)
    await session.flush()


# ===================================================================
# GET /masters/{user_id} -- success
# ===================================================================
@pytest.mark.asyncio
async def test_public_master_profile_success(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Any authenticated user can view a verified master's public profile."""
    master_auth = await _make_verified_master(client, db_session)
    master_id = master_auth["user"]["id"]

    viewer = await login_user(
        client, telegram_id=56510, first_name="Viewer",
    )
    resp = await client.get(
        f"{MASTERS_URL}/{master_id}",
        headers=auth_headers(viewer["session_token"]),
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["user_id"] == master_id
    assert data["status"] == "verified"
    assert data["display_name"] == "Alex Mindful"
    assert data["bio"] == "10 years of meditation practice."
    assert data["methods"] == ["meditation", "mindfulness"]
    assert data["experience_years"] == 10
    assert data["practices_count"] == 0
    assert data["reviews_count"] == 0


# ===================================================================
# GET /masters/{user_id} -- practices_count excludes draft/deleted
# ===================================================================
@pytest.mark.asyncio
async def test_public_master_profile_practices_count(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """practices_count counts everything except draft and deleted."""
    master_auth = await _make_verified_master(client, db_session)
    master_id = UUID(master_auth["user"]["id"])

    # Countable: scheduled, live, completed, cancelled.
    await _insert_practice(
        db_session, master_id, status=PracticeStatus.SCHEDULED.value,
    )
    await _insert_practice(
        db_session, master_id, status=PracticeStatus.LIVE.value,
    )
    await _insert_practice(
        db_session, master_id, status=PracticeStatus.COMPLETED.value,
    )
    await _insert_practice(
        db_session, master_id, status=PracticeStatus.CANCELLED.value,
    )
    # Excluded: draft, deleted.
    await _insert_practice(
        db_session, master_id, status=PracticeStatus.DRAFT.value,
    )
    await _insert_practice(
        db_session, master_id, status=PracticeStatus.DELETED.value,
    )
    await db_session.commit()

    viewer = await login_user(
        client, telegram_id=56511, first_name="Viewer",
    )
    resp = await client.get(
        f"{MASTERS_URL}/{master_auth['user']['id']}",
        headers=auth_headers(viewer["session_token"]),
    )

    assert resp.status_code == 200
    # 4 countable, 2 excluded.
    assert resp.json()["practices_count"] == 4


# ===================================================================
# GET /masters/{user_id} -- reviews_count over master's practices
# ===================================================================
@pytest.mark.asyncio
async def test_public_master_profile_reviews_count(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """reviews_count counts all feedback across the master's practices."""
    master_auth = await _make_verified_master(client, db_session)
    master_id = UUID(master_auth["user"]["id"])

    practice = await _insert_practice(
        db_session, master_id, status=PracticeStatus.COMPLETED.value,
    )

    # Two reviewers leave feedback on this master's practice.
    reviewer_a = await login_user(
        client, telegram_id=56512, first_name="ReviewerA",
    )
    reviewer_b = await login_user(
        client, telegram_id=56513, first_name="ReviewerB",
    )
    await _insert_feedback(
        db_session, practice.id, UUID(reviewer_a["user"]["id"]),
    )
    await _insert_feedback(
        db_session, practice.id, UUID(reviewer_b["user"]["id"]),
    )
    await db_session.commit()

    viewer = await login_user(
        client, telegram_id=56514, first_name="Viewer",
    )
    resp = await client.get(
        f"{MASTERS_URL}/{master_auth['user']['id']}",
        headers=auth_headers(viewer["session_token"]),
    )

    assert resp.status_code == 200
    assert resp.json()["reviews_count"] == 2


# ===================================================================
# GET /masters/{user_id} -- non-master user -> 404
# ===================================================================
@pytest.mark.asyncio
async def test_public_master_profile_non_master_404(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """A plain user id (no master profile) resolves to 404."""
    plain = await login_user(
        client, telegram_id=56520, first_name="Plain",
    )
    viewer = await login_user(
        client, telegram_id=56521, first_name="Viewer",
    )
    resp = await client.get(
        f"{MASTERS_URL}/{plain['user']['id']}",
        headers=auth_headers(viewer["session_token"]),
    )
    assert resp.status_code == 404


# ===================================================================
# GET /masters/{user_id} -- nonexistent id -> 404
# ===================================================================
@pytest.mark.asyncio
async def test_public_master_profile_nonexistent_404(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """An unknown user_id resolves to 404."""
    viewer = await login_user(
        client, telegram_id=56522, first_name="Viewer",
    )
    resp = await client.get(
        f"{MASTERS_URL}/{uuid4()}",
        headers=auth_headers(viewer["session_token"]),
    )
    assert resp.status_code == 404


# ===================================================================
# GET /masters/{user_id} -- pending master hidden -> 404
# ===================================================================
@pytest.mark.asyncio
async def test_public_master_profile_pending_404(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """A pending (unverified) master is not exposed: 404."""
    applicant = await login_user(
        client, telegram_id=56530, first_name="Applicant",
    )
    apply_resp = await client.post(
        APPLY_URL,
        json=_valid_apply_body(),
        headers=auth_headers(applicant["session_token"]),
    )
    assert apply_resp.status_code == 201  # status == pending

    viewer = await login_user(
        client, telegram_id=56531, first_name="Viewer",
    )
    resp = await client.get(
        f"{MASTERS_URL}/{applicant['user']['id']}",
        headers=auth_headers(viewer["session_token"]),
    )
    assert resp.status_code == 404


# ===================================================================
# GET /masters/{user_id} -- no auth -> 401
# ===================================================================
@pytest.mark.asyncio
async def test_public_master_profile_no_auth(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Unauthenticated request -> 401."""
    resp = await client.get(f"{MASTERS_URL}/{uuid4()}")
    assert resp.status_code == 401


# ===================================================================
# GET /masters/{user_id} -- no financial / contact leakage
# ===================================================================
@pytest.mark.asyncio
async def test_public_master_profile_no_sensitive_fields(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Public profile must not expose financial or contact data."""
    master_auth = await _make_verified_master(client, db_session)

    viewer = await login_user(
        client, telegram_id=56540, first_name="Viewer",
    )
    resp = await client.get(
        f"{MASTERS_URL}/{master_auth['user']['id']}",
        headers=auth_headers(viewer["session_token"]),
    )

    assert resp.status_code == 200
    data = resp.json()
    forbidden = {
        "frozen_cents",
        "available_cents",
        "payout",
        "min_withdrawal_cents",
        "withdrawal_fee_cents",
        "email",
        "phone",
        "certifications",
        "documents",
        "stats",
    }
    leaked = forbidden & set(data.keys())
    assert not leaked, f"sensitive fields leaked: {leaked}"


# ===================================================================
# GET /masters/me must still resolve (not shadowed by /{user_id})
# ===================================================================
@pytest.mark.asyncio
async def test_me_not_shadowed_by_dynamic_route(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """GET /masters/me returns the private profile, not a 404 / 422.

    Guards the route-ordering requirement: the dynamic /{user_id} route
    is declared after /me, so "me" is never parsed as a UUID user_id.
    """
    master_auth = await _make_verified_master(client, db_session)

    resp = await client.get(
        f"{MASTERS_URL}/me",
        headers=auth_headers(master_auth["session_token"]),
    )
    assert resp.status_code == 200
    # Private profile DOES carry financial fields -- proves it's the /me path.
    assert "available_cents" in resp.json()


# ===================================================================
# GET /practices/{id} -- master_avatar_url surfaced in detail
# ===================================================================
@pytest.mark.asyncio
async def test_practice_detail_includes_master_avatar(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Practice detail exposes the master's avatar_url."""
    master_auth = await _make_verified_master(client, db_session)
    master_id = UUID(master_auth["user"]["id"])

    # Set the avatar AFTER the last login in _make_verified_master, since
    # login upserts avatar_url from Telegram photo_url (None in tests).
    avatar = "https://t.me/i/userpic/320/master.jpg"
    await db_session.execute(
        update(User).where(User.id == master_id).values(avatar_url=avatar)
    )
    practice = await _insert_practice(
        db_session, master_id, status=PracticeStatus.SCHEDULED.value,
    )
    await db_session.commit()

    viewer = await login_user(
        client, telegram_id=56550, first_name="Viewer",
    )
    resp = await client.get(
        f"{PRACTICES_URL}/{practice.id}",
        headers=auth_headers(viewer["session_token"]),
    )

    assert resp.status_code == 200
    assert resp.json()["master_avatar_url"] == avatar


# ===================================================================
# GET /practices/{id} -- master_avatar_url is None when unset
# ===================================================================
@pytest.mark.asyncio
async def test_practice_detail_avatar_none_when_unset(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """master_avatar_url is null when the master has no avatar."""
    master_auth = await _make_verified_master(client, db_session)
    master_id = UUID(master_auth["user"]["id"])

    practice = await _insert_practice(
        db_session, master_id, status=PracticeStatus.SCHEDULED.value,
    )
    await db_session.commit()

    viewer = await login_user(
        client, telegram_id=56551, first_name="Viewer",
    )
    resp = await client.get(
        f"{PRACTICES_URL}/{practice.id}",
        headers=auth_headers(viewer["session_token"]),
    )

    assert resp.status_code == 200
    assert resp.json()["master_avatar_url"] is None
