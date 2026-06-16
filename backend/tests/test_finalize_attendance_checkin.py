# =============================================================================
# VELO Backend -- Tests: Finalize attendance by PRE check-in (W-1, variant 1)
# =============================================================================
#
# W-1: joined_at is set only via the Zoom "join" flow. While Zoom is disabled
# joined_at stays null, which would send every confirmed booking to no_show on
# finalize and block feedback / named reviews (E1). Variant 1 makes a PRE
# check-in an alternative proof of presence:
#
#   confirmed + (joined_at IS NOT NULL OR has PRE check-in) -> attended
#   confirmed + neither                                     -> no_show
#
# The rule lives in _finalize_practice_core, shared by BOTH paths -- the manual
# master finalize (finalize_practice) and the system auto-close
# (auto_finalize_practice) -- so both are covered.
#
# These tests drive the service layer directly inside one uncommitted
# transaction: domain rows are flushed (not committed) and asserted in-session,
# so cleanup only has to drop the users created via the auth API.
#
# telegram_id range: 95000-95999.
# =============================================================================

from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.bookings.models import Booking, BookingStatus
from app.modules.bookings.service import (
    auto_finalize_practice,
    finalize_practice,
)
from app.modules.diary.models import Checkin, CheckType
from app.modules.masters.models import MasterProfile
from app.modules.practices.models import (
    Practice,
    PracticeStatus,
    PracticeType,
)
from app.modules.users.models import User, UserRole
from tests.helpers import login_user

_TID_MIN = 95000
_TID_MAX = 95999


# ===================================================================
# Cleanup -- only users are committed (by the auth API); the rest is
# flushed-not-committed and disappears on rollback.
# ===================================================================


@pytest.fixture(autouse=True)
async def cleanup(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    await _do_cleanup(db_session)
    yield
    await _do_cleanup(db_session)


async def _do_cleanup(session: AsyncSession) -> None:
    await session.rollback()
    subq = select(User.id).where(User.telegram_id.between(_TID_MIN, _TID_MAX))
    await session.execute(
        MasterProfile.__table__.delete().where(MasterProfile.user_id.in_(subq))
    )
    from app.core.audit import AuditLog
    await session.execute(
        AuditLog.__table__.delete().where(AuditLog.actor_id.in_(subq))
    )
    await session.execute(
        User.__table__.delete().where(
            User.telegram_id.between(_TID_MIN, _TID_MAX)
        )
    )
    await session.commit()


# ===================================================================
# Helpers
# ===================================================================


async def _make_master(
    client: AsyncClient, db_session: AsyncSession, telegram_id: int,
) -> str:
    auth = await login_user(client, telegram_id=telegram_id, first_name="Master")
    user_id = auth["user"]["id"]
    user = await db_session.get(User, user_id)
    user.role = UserRole.MASTER
    await db_session.flush()
    db_session.add(
        MasterProfile(
            user_id=user_id,
            data={
                "account": {"status": "verified"},
                "profile": {"display_name": "Master"},
            },
        )
    )
    await db_session.flush()
    # Return the UUID (not the JSON string): practice.master_id is set from this
    # and finalize_practice compares it to User.id (UUID) in Python -- a str vs
    # UUID mismatch would wrongly fail the ownership check.
    return user.id


async def _create_practice(
    db_session: AsyncSession,
    master_id: str,
    *,
    status: str = PracticeStatus.SCHEDULED.value,
) -> Practice:
    practice = Practice(
        master_id=master_id,
        title="W1 Practice",
        description="x",
        practice_type=PracticeType.LIVE.value,
        status=status,
        scheduled_at=datetime.now(UTC) - timedelta(hours=2),
        duration_minutes=60,
        timezone="UTC",
        max_participants=10,
        current_participants=0,
        is_free=True,
        price_cents=0,
        currency="eur",
        data={},
    )
    db_session.add(practice)
    await db_session.flush()
    return practice


async def _confirmed_booking(
    client: AsyncClient,
    db_session: AsyncSession,
    practice: Practice,
    telegram_id: int,
    *,
    joined: bool = False,
) -> Booking:
    auth = await login_user(
        client, telegram_id=telegram_id, first_name=f"U{telegram_id}",
    )
    booking = Booking(
        practice_id=practice.id,
        user_id=auth["user"]["id"],
        status=BookingStatus.CONFIRMED.value,
        joined_at=(datetime.now(UTC) - timedelta(hours=1)) if joined else None,
    )
    db_session.add(booking)
    await db_session.flush()
    return booking


async def _add_pre_checkin(
    db_session: AsyncSession, practice: Practice, booking: Booking,
) -> None:
    db_session.add(
        Checkin(
            practice_id=practice.id,
            user_id=booking.user_id,
            booking_id=booking.id,
            mood=8,
            check_type=CheckType.PRE.value,
        )
    )
    await db_session.flush()


# ===================================================================
# System path -- auto_finalize_practice
# ===================================================================


@pytest.mark.asyncio
async def test_autofinalize_attendance_by_checkin_or_join(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Auto-close: PRE check-in OR Zoom join -> attended; neither -> no_show."""
    master_id = await _make_master(client, db_session, 95800)
    practice = await _create_practice(db_session, master_id)

    # A: PRE check-in, no joined_at -> attended (the W-1 case).
    b_checkin = await _confirmed_booking(client, db_session, practice, 95001)
    await _add_pre_checkin(db_session, practice, b_checkin)
    # B: joined via Zoom, no check-in -> attended (unchanged behavior).
    b_joined = await _confirmed_booking(
        client, db_session, practice, 95002, joined=True,
    )
    # C: neither -> no_show.
    b_absent = await _confirmed_booking(client, db_session, practice, 95003)

    await auto_finalize_practice(practice.id, db_session)
    await db_session.flush()

    await db_session.refresh(b_checkin)
    await db_session.refresh(b_joined)
    await db_session.refresh(b_absent)
    await db_session.refresh(practice)

    assert b_checkin.status == BookingStatus.ATTENDED.value
    assert b_joined.status == BookingStatus.ATTENDED.value
    assert b_absent.status == BookingStatus.NO_SHOW.value
    assert practice.status == PracticeStatus.COMPLETED.value


# ===================================================================
# Manual path -- finalize_practice (master)
# ===================================================================


@pytest.mark.asyncio
async def test_manual_finalize_attendance_by_checkin(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Manual master finalize uses the same rule: PRE check-in -> attended."""
    master_id = await _make_master(client, db_session, 95810)
    master_user = await db_session.get(User, master_id)
    practice = await _create_practice(db_session, master_id)

    b_checkin = await _confirmed_booking(client, db_session, practice, 95011)
    await _add_pre_checkin(db_session, practice, b_checkin)
    b_absent = await _confirmed_booking(client, db_session, practice, 95012)

    await finalize_practice(practice.id, master_user, db_session)
    await db_session.flush()

    await db_session.refresh(b_checkin)
    await db_session.refresh(b_absent)

    assert b_checkin.status == BookingStatus.ATTENDED.value
    assert b_absent.status == BookingStatus.NO_SHOW.value
