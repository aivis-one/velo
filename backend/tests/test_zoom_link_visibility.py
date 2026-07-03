# =============================================================================
# VELO Backend -- Tests: zoom_link visibility gate (M-3)
# =============================================================================
#
# telegram_id range: 96000-96999
#
# zoom_link must reach ONLY:
#   - the practice owner (a master viewing their own practice), and
#   - a user with a CONFIRMED / ATTENDED booking on the practice.
#
# Everyone else -- the public feed, a non-owner / non-booker on the detail, a
# PENDING / CANCELLED booking, and the waitlist -- gets None. The public feed
# leaking the ORM zoom_link to every authenticated user was the finding (M-3).
#
# Mechanism under test: PracticeResponse / PracticeSummary null zoom_link by
# default (a model_validator), and only the authorized paths
# (get_practice_detail for the owner/booker, GET /bookings/me for a
# confirmed/attended booking) re-set it after validation.
#
# Booking statuses are written directly (ORM) to exercise the gate independent
# of the practice lifecycle; the aggregate only cares about the row's status.
# purchases/me embeds the SAME PracticeSummary, so its zoom_link is nulled by
# the same validator as waitlist/me (covered here).
# =============================================================================

from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.bookings.models import Booking, BookingStatus
from app.modules.masters.models import MasterProfile
from app.modules.payments.models import Purchase
from app.modules.practices.models import Practice, PracticeStatus, PracticeType
from app.modules.practices.schemas import PracticeSummary, UpdatePracticeRequest
from app.modules.users.models import User, UserRole
from app.modules.waitlist.models import Waitlist, WaitlistStatus
from tests.helpers import auth_headers, login_user

FEED_URL = "/api/v1/practices"
DETAIL_URL = "/api/v1/practices/{practice_id}"
BOOKINGS_ME_URL = "/api/v1/bookings/me"
MASTER_PRACTICES_URL = "/api/v1/masters/me/practices"
WAITLIST_ME_URL = "/api/v1/waitlist/me"
PURCHASES_ME_URL = "/api/v1/purchases/me"

ZOOM = "https://zoom.example/gated-room"

# telegram_id range for this test file.
_TID_MIN = 96000
_TID_MAX = 96999


# ===================================================================
# Cleanup
# ===================================================================


async def _do_cleanup(session: AsyncSession) -> None:
    """Delete all test entities for telegram_id 96000-96999 (FK-safe order)."""
    await session.rollback()

    user_ids_subq = select(User.id).where(
        User.telegram_id.between(_TID_MIN, _TID_MAX),
    )

    # audit_logs for our users (role change / master verification may write).
    from app.core.audit import AuditLog
    await session.execute(
        AuditLog.__table__.delete().where(
            AuditLog.actor_id.in_(user_ids_subq),
        )
    )
    # purchases have RESTRICT FKs to user / practice / booking -> they must be
    # deleted BEFORE any of those, or the delete is blocked.
    await session.execute(
        Purchase.__table__.delete().where(
            Purchase.user_id.in_(user_ids_subq),
        )
    )
    # bookings + waitlist reference practices AND users -> delete before both.
    await session.execute(
        Booking.__table__.delete().where(
            Booking.user_id.in_(user_ids_subq),
        )
    )
    await session.execute(
        Waitlist.__table__.delete().where(
            Waitlist.user_id.in_(user_ids_subq),
        )
    )
    # practices reference master_profiles (users).
    await session.execute(
        Practice.__table__.delete().where(
            Practice.master_id.in_(user_ids_subq),
        )
    )
    await session.execute(
        MasterProfile.__table__.delete().where(
            MasterProfile.user_id.in_(user_ids_subq),
        )
    )
    await session.execute(
        User.__table__.delete().where(
            User.telegram_id.between(_TID_MIN, _TID_MAX),
        )
    )
    await session.commit()


@pytest.fixture(autouse=True)
async def cleanup(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    """Clean test data before/after each test in FK-safe order."""
    await _do_cleanup(db_session)
    yield
    await _do_cleanup(db_session)


# ===================================================================
# Helpers
# ===================================================================


async def _make_verified_master(
    client: AsyncClient,
    db_session: AsyncSession,
    telegram_id: int,
) -> dict:
    """Create a verified master and return the auth dict."""
    auth = await login_user(client, telegram_id=telegram_id, first_name="Master")
    user_id = auth["user"]["id"]

    user = await db_session.get(User, user_id)
    user.role = UserRole.MASTER
    await db_session.flush()

    profile = MasterProfile(
        user_id=user_id,
        data={
            "account": {"status": "verified"},
            "profile": {"bio": "Test master"},
        },
    )
    db_session.add(profile)
    await db_session.flush()

    return auth


async def _create_practice(
    db_session: AsyncSession,
    master_id: str,
    *,
    zoom_link: str | None,
    status: str = PracticeStatus.SCHEDULED.value,
    title: str = "Zoom Gate Practice",
) -> Practice:
    """Create a practice carrying a zoom_link.

    Defaults to a SCHEDULED future practice so it shows in the default
    (future-only) public feed.
    """
    scheduled_at = (
        datetime.now(UTC) + timedelta(days=3)
        if status == PracticeStatus.SCHEDULED.value
        else datetime.now(UTC) - timedelta(hours=3)
    )
    practice = Practice(
        master_id=master_id,
        title=title,
        description="Zoom gate testing",
        practice_type=PracticeType.LIVE.value,
        status=status,
        scheduled_at=scheduled_at,
        duration_minutes=60,
        timezone="UTC",
        max_participants=20,
        current_participants=0,
        is_free=True,
        price_cents=0,
        currency="eur",
        zoom_link=zoom_link,
    )
    db_session.add(practice)
    await db_session.flush()
    return practice


async def _add_booking(
    db_session: AsyncSession,
    client: AsyncClient,
    practice: Practice,
    telegram_id: int,
    *,
    status: str,
) -> dict:
    """Register a user with a booking in the given status (direct ORM write)."""
    auth = await login_user(
        client, telegram_id=telegram_id, first_name=f"U{telegram_id}",
    )
    booking = Booking(
        practice_id=practice.id,
        user_id=auth["user"]["id"],
        status=status,
        # joined_at is nullable (set on join); a timestamp only where it is
        # natural (attended), None otherwise. Irrelevant to the zoom gate.
        joined_at=(
            datetime.now(UTC) - timedelta(hours=1)
            if status == BookingStatus.ATTENDED.value
            else None
        ),
    )
    db_session.add(booking)
    await db_session.flush()
    return auth


def _find_in_feed(items: list[dict], practice_id: object) -> dict:
    """Return the feed item (a practice) for a given practice id."""
    target = str(practice_id)
    for item in items:
        if item["id"] == target:
            return item
    raise AssertionError(f"practice {target} not in feed items")


# ===================================================================
# Public feed -- never exposes zoom_link
# ===================================================================


@pytest.mark.asyncio
async def test_public_feed_hides_zoom_link(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """GET /practices leaves zoom_link None even though the ORM row has one."""
    master = await _make_verified_master(client, db_session, telegram_id=96100)
    practice = await _create_practice(
        db_session, master["user"]["id"], zoom_link=ZOOM,
    )
    await db_session.commit()

    viewer = await login_user(client, telegram_id=96110, first_name="Viewer")
    resp = await client.get(
        f"{FEED_URL}?master_id={master['user']['id']}",
        headers=auth_headers(viewer["session_token"]),
    )

    assert resp.status_code == 200
    item = _find_in_feed(resp.json()["items"], practice.id)
    assert item["zoom_link"] is None


# ===================================================================
# Detail -- owner always sees zoom_link
# ===================================================================


@pytest.mark.asyncio
async def test_owner_detail_shows_zoom_link(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """The practice owner sees the real zoom_link on the detail."""
    master = await _make_verified_master(client, db_session, telegram_id=96200)
    practice = await _create_practice(
        db_session, master["user"]["id"], zoom_link=ZOOM,
    )
    await db_session.commit()

    resp = await client.get(
        DETAIL_URL.format(practice_id=practice.id),
        headers=auth_headers(master["session_token"]),
    )

    assert resp.status_code == 200
    assert resp.json()["zoom_link"] == ZOOM


# ===================================================================
# Detail -- gated by the requester's booking status
# ===================================================================


@pytest.mark.asyncio
async def test_detail_zoom_link_gated_by_booking(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """On the detail, only a confirmed booker sees zoom_link.

    A pending booker and a total stranger both get None.
    """
    master = await _make_verified_master(client, db_session, telegram_id=96300)
    practice = await _create_practice(
        db_session, master["user"]["id"], zoom_link=ZOOM,
    )
    confirmed = await _add_booking(
        db_session, client, practice, 96301,
        status=BookingStatus.CONFIRMED.value,
    )
    pending = await _add_booking(
        db_session, client, practice, 96302,
        status=BookingStatus.PENDING.value,
    )
    await db_session.commit()

    stranger = await login_user(client, telegram_id=96303, first_name="Stranger")
    url = DETAIL_URL.format(practice_id=practice.id)

    r_confirmed = await client.get(
        url, headers=auth_headers(confirmed["session_token"]),
    )
    r_pending = await client.get(
        url, headers=auth_headers(pending["session_token"]),
    )
    r_stranger = await client.get(
        url, headers=auth_headers(stranger["session_token"]),
    )

    assert r_confirmed.status_code == 200
    assert r_confirmed.json()["zoom_link"] == ZOOM
    assert r_pending.json()["zoom_link"] is None
    assert r_stranger.json()["zoom_link"] is None


# ===================================================================
# GET /bookings/me -- gated by the booking's own status
# ===================================================================


@pytest.mark.asyncio
async def test_bookings_me_zoom_link_gated_by_status(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """On the dashboard feed, zoom_link shows for confirmed/attended only.

    Each user has a single booking; GET /bookings/me returns it with the
    embedded PracticeSummary. pending / cancelled -> None.
    """
    master = await _make_verified_master(client, db_session, telegram_id=96400)
    practice = await _create_practice(
        db_session, master["user"]["id"], zoom_link=ZOOM,
    )
    confirmed = await _add_booking(
        db_session, client, practice, 96401,
        status=BookingStatus.CONFIRMED.value,
    )
    attended = await _add_booking(
        db_session, client, practice, 96402,
        status=BookingStatus.ATTENDED.value,
    )
    pending = await _add_booking(
        db_session, client, practice, 96403,
        status=BookingStatus.PENDING.value,
    )
    cancelled = await _add_booking(
        db_session, client, practice, 96404,
        status=BookingStatus.CANCELLED.value,
    )
    await db_session.commit()

    async def _zoom_of(auth: dict) -> object:
        resp = await client.get(
            BOOKINGS_ME_URL, headers=auth_headers(auth["session_token"]),
        )
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert len(items) == 1
        return items[0]["practice"]["zoom_link"]

    assert await _zoom_of(confirmed) == ZOOM
    assert await _zoom_of(attended) == ZOOM
    assert await _zoom_of(pending) is None
    assert await _zoom_of(cancelled) is None


# ===================================================================
# GET /waitlist/me -- never exposes zoom_link
# ===================================================================


@pytest.mark.asyncio
async def test_waitlist_me_hides_zoom_link(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """A waitlisted user (no confirmed booking) never sees zoom_link."""
    master = await _make_verified_master(client, db_session, telegram_id=96500)
    practice = await _create_practice(
        db_session, master["user"]["id"], zoom_link=ZOOM,
    )
    waiter = await login_user(client, telegram_id=96501, first_name="Waiter")
    db_session.add(
        Waitlist(
            practice_id=practice.id,
            user_id=waiter["user"]["id"],
            position=1,
            status=WaitlistStatus.WAITING.value,
            joined_at=datetime.now(UTC),
        )
    )
    await db_session.flush()
    await db_session.commit()

    resp = await client.get(
        WAITLIST_ME_URL, headers=auth_headers(waiter["session_token"]),
    )

    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) == 1
    assert items[0]["practice"]["zoom_link"] is None


# ===================================================================
# zoom_link format validation (M-3 hardening): non-https is rejected
# ===================================================================


@pytest.mark.asyncio
async def test_zoom_link_format_rejects_non_https() -> None:
    """The backend rejects a manually-entered zoom_link that is not https://.

    The frontend guards this on the create form, but the backend is the source
    of truth: a direct API call must not be able to store a non-https /
    javascript: link. Empty / None / https:// are accepted.
    """
    for bad in (
        "http://insecure.example/j/1",
        "javascript:alert(1)",
        "ftp://x",
        "zoom.us/j/1",
    ):
        with pytest.raises(ValidationError):
            UpdatePracticeRequest(zoom_link=bad)

    # Accepted: a proper https link, plus "no link" (empty / None).
    assert (
        UpdatePracticeRequest(zoom_link="https://zoom.us/j/123").zoom_link
        == "https://zoom.us/j/123"
    )
    assert UpdatePracticeRequest(zoom_link=None).zoom_link is None
    assert UpdatePracticeRequest(zoom_link="").zoom_link == ""


# ===================================================================
# Z-6 regression: the master's OWN list exposes zoom_link to the owner
# ===================================================================


@pytest.mark.asyncio
async def test_master_own_list_shows_zoom_link(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """GET /masters/me/practices exposes zoom_link to the owning master.

    Every row in the master's own list is owned by the requester, so the
    dashboard "Войти" button must receive the real link. Guards against the
    fail-open trap of dropping zoom_link_visible=True on this builder (Z-6).
    """
    master = await _make_verified_master(client, db_session, telegram_id=96600)
    practice = await _create_practice(
        db_session, master["user"]["id"], zoom_link=ZOOM,
    )
    await db_session.commit()

    resp = await client.get(
        MASTER_PRACTICES_URL,
        headers=auth_headers(master["session_token"]),
    )

    assert resp.status_code == 200
    item = _find_in_feed(resp.json()["items"], practice.id)
    assert item["zoom_link"] == ZOOM


# ===================================================================
# Z-7 factory: PracticeSummary.from_practice is fail-closed on zoom_link
# ===================================================================


@pytest.mark.asyncio
async def test_summary_factory_zoom_link_fail_closed(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """The single summary factory nulls zoom_link unless explicitly opened.

    This is the fail-closed backstop (Z-7): from_practice() defaults
    zoom_link to None even though the ORM row carries one, and only surfaces
    it when the caller passes zoom_link_visible=True.
    """
    master = await _make_verified_master(client, db_session, telegram_id=96900)
    practice = await _create_practice(
        db_session, master["user"]["id"], zoom_link=ZOOM,
    )
    await db_session.flush()

    # Default (no flag) -> fail-closed: zoom_link is None; master_name is set.
    closed = PracticeSummary.from_practice(practice, master_name="M")
    assert closed.zoom_link is None
    assert closed.master_name == "M"

    # Explicit opt-in -> the real link.
    opened = PracticeSummary.from_practice(
        practice, master_name="M", zoom_link_visible=True,
    )
    assert opened.zoom_link == ZOOM


# ===================================================================
# purchases/me -- never exposes zoom_link (third PracticeSummary consumer)
# ===================================================================


@pytest.mark.asyncio
async def test_purchases_me_hides_zoom_link(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """GET /purchases/me leaves zoom_link None even for a confirmed booking.

    Purchase history is not a zoom entry point (and a purchase can outlive a
    cancelled / refunded booking), so the link is never surfaced there --
    even though the buyer here holds a CONFIRMED booking.
    """
    master = await _make_verified_master(client, db_session, telegram_id=96950)
    practice = await _create_practice(
        db_session, master["user"]["id"], zoom_link=ZOOM,
    )
    buyer = await login_user(client, telegram_id=96951, first_name="Buyer")

    booking = Booking(
        practice_id=practice.id,
        user_id=buyer["user"]["id"],
        status=BookingStatus.CONFIRMED.value,
        joined_at=None,
    )
    db_session.add(booking)
    await db_session.flush()
    # Direct Purchase row (defaults: amounts 0, status pending, currency eur).
    # No ledger is needed -- purchases/me reads only Purchase + Practice.
    purchase = Purchase(
        user_id=buyer["user"]["id"],
        practice_id=practice.id,
        booking_id=booking.id,
    )
    db_session.add(purchase)
    await db_session.flush()
    await db_session.commit()

    resp = await client.get(
        PURCHASES_ME_URL, headers=auth_headers(buyer["session_token"]),
    )

    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) == 1
    assert items[0]["practice"]["zoom_link"] is None
