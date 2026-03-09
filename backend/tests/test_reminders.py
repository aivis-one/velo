from collections.abc import AsyncGenerator
# =============================================================================
# Test: Reminders -- Phase 7.4
# =============================================================================
#
# Tests cover:
#   1. schedule_reminders() -- user reminders for bookings
#   2. schedule_master_reminders() -- master reminders on draft->scheduled
#   3. cancel_reminders_for_booking() -- cancel user reminders on cancel
#   4. cancel_all_reminders_for_practice() -- bulk cancel on practice cancel
#   5. reschedule_reminders_for_practice() -- cancel + recreate on time change
#   6. Skipping past reminders (practice soon)
#   7. Integration: create_booking triggers reminders
#   8. Integration: cancel_booking cancels reminders
#   9. Integration: update_practice draft->scheduled triggers master reminders
#  10. Integration: update_practice scheduled_at change triggers reschedule
#
# telegram_id range: 84000-84999
# =============================================================================

from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from sqlalchemy import select, func, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.bookings.models import Booking, BookingStatus
from app.modules.masters.models import MasterProfile
from app.modules.notifications.models import (
    Notification,
    NotificationStatus,
    NotificationType,
    TargetType,
)
from app.modules.notifications.reminders import (
    _ALL_MASTER_REMINDER_TYPES,
    _ALL_REMINDER_TYPES,
    _ALL_USER_REMINDER_TYPES,
    cancel_all_reminders_for_practice,
    cancel_reminders_for_booking,
    reschedule_reminders_for_practice,
    schedule_master_reminders,
    schedule_reminders,
)
from app.modules.practices.models import Practice, PracticeStatus, PracticeType
from app.modules.users.models import User, UserRole


# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------


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
    """Full ORM cleanup for telegram_id 84000-84999."""
    await full_cleanup_range(session, 84000, 84999, delete_users=True)
    await session.commit()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _create_user(
    session: AsyncSession,
    telegram_id: int,
    role: str = UserRole.USER.value,
    first_name: str | None = None,
) -> User:
    """Create a user directly in DB."""
    user = User(
        telegram_id=telegram_id,
        first_name=first_name or f"User{telegram_id}",
        role=role,
    )
    session.add(user)
    await session.flush()
    await session.refresh(user)
    return user


async def _create_master_with_profile(
    session: AsyncSession,
    telegram_id: int,
    display_name: str = "Test Master",
) -> tuple[User, MasterProfile]:
    """Create a verified master with profile."""
    user = await _create_user(
        session, telegram_id,
        role=UserRole.MASTER.value,
        first_name=display_name,
    )
    profile = MasterProfile(
        user_id=user.id,
        data={
            "account": {"status": "verified"},
            "profile": {"display_name": display_name},
        },
    )
    session.add(profile)
    await session.flush()
    await session.refresh(profile)
    return user, profile


async def _create_practice(
    session: AsyncSession,
    master: User,
    *,
    hours_ahead: int = 48,
    status: str = PracticeStatus.SCHEDULED.value,
) -> Practice:
    """Create a practice scheduled hours_ahead from now."""
    practice = Practice(
        master_id=master.id,
        practice_type=PracticeType.LIVE.value,
        status=status,
        title="Test Meditation",
        scheduled_at=datetime.now(UTC) + timedelta(hours=hours_ahead),
        duration_minutes=60,
        timezone="UTC",
        is_free=True,
        price_cents=0,
        currency="EUR",
    )
    session.add(practice)
    await session.flush()
    await session.refresh(practice)
    return practice


async def _create_booking(
    session: AsyncSession,
    user: User,
    practice: Practice,
) -> Booking:
    """Create a confirmed booking directly in DB."""
    booking = Booking(
        practice_id=practice.id,
        user_id=user.id,
        status=BookingStatus.CONFIRMED.value,
    )
    session.add(booking)
    await session.flush()
    await session.refresh(booking)
    return booking


async def _count_reminders(
    session: AsyncSession,
    practice_id: UUID,
    *,
    status: str | None = None,
    types: set[str] | None = None,
) -> int:
    """Count reminder notifications for a practice."""
    filters = [
        Notification.action_data["practice_id"].astext == str(practice_id),
    ]
    if types:
        filters.append(Notification.type.in_(types))
    else:
        filters.append(Notification.type.in_(_ALL_REMINDER_TYPES))

    if status:
        filters.append(Notification.status == status)

    stmt = select(func.count(Notification.id)).where(*filters)
    result = await session.execute(stmt)
    return result.scalar_one()


# ===================================================================
# 1. schedule_reminders (user)
# ===================================================================


class TestScheduleReminders:
    """Tests for schedule_reminders() -- user reminders."""

    @pytest.mark.asyncio
    async def test_creates_3_reminders_for_future_practice(
        self, db_session: AsyncSession,
    ) -> None:
        """Practice 48h away: all 3 reminders created."""
        master, _ = await _create_master_with_profile(
            db_session, telegram_id=84001,
        )
        user = await _create_user(db_session, telegram_id=84002)
        practice = await _create_practice(
            db_session, master, hours_ahead=48,
        )
        booking = await _create_booking(db_session, user, practice)

        reminders = await schedule_reminders(
            booking, practice, user, db_session,
        )

        assert len(reminders) == 3
        types = {r.type for r in reminders}
        assert types == {
            NotificationType.REMINDER_24H.value,
            NotificationType.REMINDER_1H.value,
            NotificationType.REMINDER_10MIN.value,
        }

        # All target this specific user.
        for r in reminders:
            assert r.target_type == TargetType.USER.value
            assert r.target_value == str(user.id)
            assert r.status == NotificationStatus.PENDING.value
            assert r.priority == 2
            assert r.expiry_at == practice.scheduled_at
            assert r.action_data["practice_id"] == str(practice.id)
            assert r.action_data["practice_title"] == "Test Meditation"

    @pytest.mark.asyncio
    async def test_skips_past_reminders(
        self, db_session: AsyncSession,
    ) -> None:
        """Practice 30min away: only 10min reminder created."""
        master, _ = await _create_master_with_profile(
            db_session, telegram_id=84003,
        )
        user = await _create_user(db_session, telegram_id=84004)
        # 30 min ahead: 24h and 1h reminders are in the past.
        practice = await _create_practice(
            db_session, master, hours_ahead=0,
        )
        # Override scheduled_at to 30 minutes from now.
        practice.scheduled_at = datetime.now(UTC) + timedelta(minutes=30)
        await db_session.flush()

        booking = await _create_booking(db_session, user, practice)

        reminders = await schedule_reminders(
            booking, practice, user, db_session,
        )

        assert len(reminders) == 1
        assert reminders[0].type == NotificationType.REMINDER_10MIN.value

    @pytest.mark.asyncio
    async def test_no_reminders_when_practice_imminent(
        self, db_session: AsyncSession,
    ) -> None:
        """Practice 3min away: no reminders created."""
        master, _ = await _create_master_with_profile(
            db_session, telegram_id=84005,
        )
        user = await _create_user(db_session, telegram_id=84006)
        practice = await _create_practice(
            db_session, master, hours_ahead=0,
        )
        practice.scheduled_at = datetime.now(UTC) + timedelta(minutes=3)
        await db_session.flush()

        booking = await _create_booking(db_session, user, practice)

        reminders = await schedule_reminders(
            booking, practice, user, db_session,
        )

        assert len(reminders) == 0

    @pytest.mark.asyncio
    async def test_action_data_contains_master_name(
        self, db_session: AsyncSession,
    ) -> None:
        """Reminder action_data includes master display name."""
        master, _ = await _create_master_with_profile(
            db_session, telegram_id=84007,
            display_name="Guru Yogi",
        )
        user = await _create_user(db_session, telegram_id=84008)
        practice = await _create_practice(
            db_session, master, hours_ahead=48,
        )
        booking = await _create_booking(db_session, user, practice)

        reminders = await schedule_reminders(
            booking, practice, user, db_session,
        )

        assert reminders[0].action_data["master_name"] == "Guru Yogi"

    @pytest.mark.asyncio
    async def test_two_hours_ahead_creates_two_reminders(
        self, db_session: AsyncSession,
    ) -> None:
        """Practice 2h away: 1h and 10min reminders created."""
        master, _ = await _create_master_with_profile(
            db_session, telegram_id=84009,
        )
        user = await _create_user(db_session, telegram_id=84010)
        practice = await _create_practice(
            db_session, master, hours_ahead=2,
        )
        booking = await _create_booking(db_session, user, practice)

        reminders = await schedule_reminders(
            booking, practice, user, db_session,
        )

        assert len(reminders) == 2
        types = {r.type for r in reminders}
        assert NotificationType.REMINDER_24H.value not in types
        assert NotificationType.REMINDER_1H.value in types
        assert NotificationType.REMINDER_10MIN.value in types


# ===================================================================
# 2. schedule_master_reminders
# ===================================================================


class TestScheduleMasterReminders:
    """Tests for schedule_master_reminders()."""

    @pytest.mark.asyncio
    async def test_creates_3_master_reminders(
        self, db_session: AsyncSession,
    ) -> None:
        """Practice 48h away: all 3 master reminders."""
        master, _ = await _create_master_with_profile(
            db_session, telegram_id=84020,
        )
        practice = await _create_practice(
            db_session, master, hours_ahead=48,
        )

        reminders = await schedule_master_reminders(
            practice, db_session,
        )

        assert len(reminders) == 3
        types = {r.type for r in reminders}
        assert types == {
            NotificationType.MASTER_REMINDER_24H.value,
            NotificationType.MASTER_REMINDER_1H.value,
            NotificationType.MASTER_REMINDER_10MIN.value,
        }

        # All target the master.
        for r in reminders:
            assert r.target_value == str(master.id)
            assert r.action_data["participants_count"] is not None

    @pytest.mark.asyncio
    async def test_master_reminder_includes_participant_count(
        self, db_session: AsyncSession,
    ) -> None:
        """Master reminder action_data has participants_count."""
        master, _ = await _create_master_with_profile(
            db_session, telegram_id=84021,
        )
        practice = await _create_practice(
            db_session, master, hours_ahead=48,
        )

        # Add 2 bookings.
        for tid in (84022, 84023):
            user = await _create_user(db_session, telegram_id=tid)
            await _create_booking(db_session, user, practice)

        reminders = await schedule_master_reminders(
            practice, db_session,
        )

        assert reminders[0].action_data["participants_count"] == "2"

    @pytest.mark.asyncio
    async def test_master_reminder_skips_past(
        self, db_session: AsyncSession,
    ) -> None:
        """Practice 30min away: only 10min master reminder."""
        master, _ = await _create_master_with_profile(
            db_session, telegram_id=84024,
        )
        practice = await _create_practice(
            db_session, master, hours_ahead=0,
        )
        practice.scheduled_at = datetime.now(UTC) + timedelta(minutes=30)
        await db_session.flush()

        reminders = await schedule_master_reminders(
            practice, db_session,
        )

        assert len(reminders) == 1
        assert reminders[0].type == NotificationType.MASTER_REMINDER_10MIN.value


# ===================================================================
# 3. cancel_reminders_for_booking
# ===================================================================


class TestCancelRemindersForBooking:
    """Tests for cancel_reminders_for_booking()."""

    @pytest.mark.asyncio
    async def test_cancels_user_reminders(
        self, db_session: AsyncSession,
    ) -> None:
        """Cancels only this user's reminders for this practice."""
        master, _ = await _create_master_with_profile(
            db_session, telegram_id=84030,
        )
        user = await _create_user(db_session, telegram_id=84031)
        practice = await _create_practice(
            db_session, master, hours_ahead=48,
        )
        booking = await _create_booking(db_session, user, practice)

        await schedule_reminders(booking, practice, user, db_session)

        # Verify 3 pending.
        count_before = await _count_reminders(
            db_session, practice.id,
            status=NotificationStatus.PENDING.value,
            types=_ALL_USER_REMINDER_TYPES,
        )
        assert count_before == 3

        # Cancel.
        expired = await cancel_reminders_for_booking(
            user.id, practice.id, db_session,
        )
        assert expired == 3

        # All expired now.
        count_after = await _count_reminders(
            db_session, practice.id,
            status=NotificationStatus.PENDING.value,
            types=_ALL_USER_REMINDER_TYPES,
        )
        assert count_after == 0

    @pytest.mark.asyncio
    async def test_does_not_cancel_master_reminders(
        self, db_session: AsyncSession,
    ) -> None:
        """cancel_reminders_for_booking does NOT touch master reminders."""
        master, _ = await _create_master_with_profile(
            db_session, telegram_id=84032,
        )
        user = await _create_user(db_session, telegram_id=84033)
        practice = await _create_practice(
            db_session, master, hours_ahead=48,
        )
        booking = await _create_booking(db_session, user, practice)

        await schedule_reminders(booking, practice, user, db_session)
        await schedule_master_reminders(practice, db_session)

        # Cancel user reminders.
        await cancel_reminders_for_booking(
            user.id, practice.id, db_session,
        )

        # Master reminders still pending.
        master_count = await _count_reminders(
            db_session, practice.id,
            status=NotificationStatus.PENDING.value,
            types=_ALL_MASTER_REMINDER_TYPES,
        )
        assert master_count == 3

    @pytest.mark.asyncio
    async def test_does_not_cancel_other_users_reminders(
        self, db_session: AsyncSession,
    ) -> None:
        """Cancelling user1's reminders does not affect user2's."""
        master, _ = await _create_master_with_profile(
            db_session, telegram_id=84034,
        )
        user1 = await _create_user(db_session, telegram_id=84035)
        user2 = await _create_user(db_session, telegram_id=84036)
        practice = await _create_practice(
            db_session, master, hours_ahead=48,
        )
        booking1 = await _create_booking(db_session, user1, practice)
        booking2 = await _create_booking(db_session, user2, practice)

        await schedule_reminders(booking1, practice, user1, db_session)
        await schedule_reminders(booking2, practice, user2, db_session)

        # Cancel user1's only.
        await cancel_reminders_for_booking(
            user1.id, practice.id, db_session,
        )

        # user2's reminders still pending.
        stmt = (
            select(func.count(Notification.id))
            .where(
                Notification.target_value == str(user2.id),
                Notification.status == NotificationStatus.PENDING.value,
                Notification.type.in_(_ALL_USER_REMINDER_TYPES),
            )
        )
        result = await db_session.execute(stmt)
        assert result.scalar_one() == 3


# ===================================================================
# 4. cancel_all_reminders_for_practice
# ===================================================================


class TestCancelAllRemindersForPractice:
    """Tests for cancel_all_reminders_for_practice()."""

    @pytest.mark.asyncio
    async def test_cancels_user_and_master_reminders(
        self, db_session: AsyncSession,
    ) -> None:
        """Cancels both user and master reminders."""
        master, _ = await _create_master_with_profile(
            db_session, telegram_id=84040,
        )
        user = await _create_user(db_session, telegram_id=84041)
        practice = await _create_practice(
            db_session, master, hours_ahead=48,
        )
        booking = await _create_booking(db_session, user, practice)

        await schedule_reminders(booking, practice, user, db_session)
        await schedule_master_reminders(practice, db_session)

        # 6 total (3 user + 3 master).
        total_before = await _count_reminders(
            db_session, practice.id,
            status=NotificationStatus.PENDING.value,
        )
        assert total_before == 6

        expired = await cancel_all_reminders_for_practice(
            practice.id, db_session,
        )
        assert expired == 6

        total_after = await _count_reminders(
            db_session, practice.id,
            status=NotificationStatus.PENDING.value,
        )
        assert total_after == 0


# ===================================================================
# 5. reschedule_reminders_for_practice
# ===================================================================


class TestRescheduleReminders:
    """Tests for reschedule_reminders_for_practice()."""

    @pytest.mark.asyncio
    async def test_reschedule_cancels_old_creates_new(
        self, db_session: AsyncSession,
    ) -> None:
        """Reschedule: old reminders expired, new ones created."""
        master, _ = await _create_master_with_profile(
            db_session, telegram_id=84050,
        )
        user = await _create_user(db_session, telegram_id=84051)
        practice = await _create_practice(
            db_session, master, hours_ahead=48,
        )
        booking = await _create_booking(db_session, user, practice)

        await schedule_reminders(booking, practice, user, db_session)
        await schedule_master_reminders(practice, db_session)

        # Change scheduled_at.
        practice.scheduled_at = datetime.now(UTC) + timedelta(hours=72)
        await db_session.flush()

        total_new = await reschedule_reminders_for_practice(
            practice, db_session,
        )

        # Should have created 6 new (3 master + 3 user).
        assert total_new == 6

        # Old ones expired.
        expired_count = await _count_reminders(
            db_session, practice.id,
            status=NotificationStatus.EXPIRED.value,
        )
        assert expired_count == 6

        # New ones pending.
        pending_count = await _count_reminders(
            db_session, practice.id,
            status=NotificationStatus.PENDING.value,
        )
        assert pending_count == 6

    @pytest.mark.asyncio
    async def test_reschedule_with_multiple_bookings(
        self, db_session: AsyncSession,
    ) -> None:
        """Reschedule creates reminders for all active bookings."""
        master, _ = await _create_master_with_profile(
            db_session, telegram_id=84052,
        )
        practice = await _create_practice(
            db_session, master, hours_ahead=48,
        )

        # 3 users with bookings.
        for tid in (84053, 84054, 84055):
            user = await _create_user(db_session, telegram_id=tid)
            booking = await _create_booking(db_session, user, practice)
            await schedule_reminders(booking, practice, user, db_session)

        await schedule_master_reminders(practice, db_session)

        # 12 total (9 user + 3 master).
        assert await _count_reminders(
            db_session, practice.id,
            status=NotificationStatus.PENDING.value,
        ) == 12

        # Reschedule.
        practice.scheduled_at = datetime.now(UTC) + timedelta(hours=72)
        await db_session.flush()

        total_new = await reschedule_reminders_for_practice(
            practice, db_session,
        )

        # 12 new (9 user + 3 master).
        assert total_new == 12

        # 12 expired + 12 pending = 24 total.
        total = await _count_reminders(db_session, practice.id)
        assert total == 24


# ===================================================================
# 6. Edge cases
# ===================================================================


class TestEdgeCases:
    """Edge case tests."""

    @pytest.mark.asyncio
    async def test_cancel_nonexistent_reminders(
        self, db_session: AsyncSession,
    ) -> None:
        """Cancelling reminders that don't exist returns 0."""
        from uuid import uuid4

        expired = await cancel_reminders_for_booking(
            uuid4(), uuid4(), db_session,
        )
        assert expired == 0

    @pytest.mark.asyncio
    async def test_master_name_fallback_to_first_name(
        self, db_session: AsyncSession,
    ) -> None:
        """When MasterProfile has no display_name, falls back to first_name."""
        user = await _create_user(
            db_session, telegram_id=84060,
            role=UserRole.MASTER.value,
            first_name="Svetlana",
        )
        # Profile without display_name in data.profile.
        profile = MasterProfile(
            user_id=user.id,
            data={"account": {"status": "verified"}},
        )
        db_session.add(profile)
        await db_session.flush()

        practice = await _create_practice(
            db_session, user, hours_ahead=48,
        )
        booker = await _create_user(db_session, telegram_id=84061)
        booking = await _create_booking(db_session, booker, practice)

        reminders = await schedule_reminders(
            booking, practice, booker, db_session,
        )

        assert reminders[0].action_data["master_name"] == "Svetlana"

    @pytest.mark.asyncio
    async def test_idempotent_cancel(
        self, db_session: AsyncSession,
    ) -> None:
        """Double cancel returns 0 on second call."""
        master, _ = await _create_master_with_profile(
            db_session, telegram_id=84062,
        )
        user = await _create_user(db_session, telegram_id=84063)
        practice = await _create_practice(
            db_session, master, hours_ahead=48,
        )
        booking = await _create_booking(db_session, user, practice)

        await schedule_reminders(booking, practice, user, db_session)

        first = await cancel_reminders_for_booking(
            user.id, practice.id, db_session,
        )
        assert first == 3

        second = await cancel_reminders_for_booking(
            user.id, practice.id, db_session,
        )
        assert second == 0
