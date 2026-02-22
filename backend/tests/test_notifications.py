# =============================================================================
# Test: Notifications Module — Phase 7.2
# =============================================================================
#
# Tests cover:
#   1. create_notification() helper
#   2. Target resolution (user, practice, role)
#   3. Delivery processing (stub formatter, status transitions)
#   4. Retry logic (attempts < max → pending, >= max → failed)
#   5. Expiry (expired notifications skip delivery)
#   6. Rollup (notification status based on deliveries)
#
# telegram_id range: 83000-83999
# =============================================================================

from datetime import UTC, datetime, timedelta
from unittest.mock import patch
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.bookings.models import Booking, BookingStatus
from app.modules.masters.models import MasterProfile
from app.modules.notifications.formatters import DeliveryResult, StubFormatter
from app.modules.notifications.models import (
    DeliveryChannel,
    DeliveryStatus,
    Notification,
    NotificationDelivery,
    NotificationStatus,
    NotificationType,
    TargetType,
)
from app.modules.notifications.processor import (
    _stage_deliver,
    _stage_resolve,
    _stage_rollup,
)
from app.modules.notifications.service import (
    create_notification,
    resolve_notification,
)
from app.modules.practices.models import Practice, PracticeStatus, PracticeType
from app.modules.users.models import User, UserRole
from tests.helpers import auth_headers, login_user


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
async def cleanup_notifications(db_session: AsyncSession):
    """Clean up all test entities before and after each test.

    Covers: notification_deliveries, notifications, bookings,
    practices, master_profiles, users (telegram_id 83000-83999).
    Before+after pattern protects against interrupted previous runs.
    """
    await _do_cleanup(db_session)
    yield
    await _do_cleanup(db_session)


async def _do_cleanup(session: AsyncSession) -> None:
    """Delete all test entities in FK-safe order."""
    await session.rollback()

    # 1. notification_deliveries (FK → notifications, users).
    await session.execute(
        NotificationDelivery.__table__.delete()
    )
    # 2. notifications.
    await session.execute(
        Notification.__table__.delete()
    )
    # 3. bookings where user is in our telegram_id range.
    user_ids_subq = (
        select(User.id).where(
            User.telegram_id.between(83000, 83999),
        )
    )
    await session.execute(
        Booking.__table__.delete().where(
            Booking.user_id.in_(user_ids_subq),
        )
    )
    # 4. practices where master is in our range.
    await session.execute(
        Practice.__table__.delete().where(
            Practice.master_id.in_(user_ids_subq),
        )
    )
    # 5. master_profiles where user is in our range.
    await session.execute(
        MasterProfile.__table__.delete().where(
            MasterProfile.user_id.in_(user_ids_subq),
        )
    )
    # 6. users in our telegram_id range.
    await session.execute(
        User.__table__.delete().where(
            User.telegram_id.between(83000, 83999),
        )
    )
    await session.commit()


# ---------------------------------------------------------------------------
# Helper: create a user directly in DB
# ---------------------------------------------------------------------------


async def _create_user(
    session: AsyncSession,
    telegram_id: int,
    role: str = UserRole.USER.value,
) -> User:
    """Create a user directly in DB for notification tests."""
    user = User(
        telegram_id=telegram_id,
        first_name=f"User{telegram_id}",
        role=role,
    )
    session.add(user)
    await session.flush()
    await session.refresh(user)
    return user


# ===================================================================
# 1. create_notification() helper
# ===================================================================


class TestCreateNotification:
    """Tests for the create_notification() service function."""

    @pytest.mark.asyncio
    async def test_creates_pending_notification(
        self,
        db_session: AsyncSession,
        cleanup_notifications,
    ) -> None:
        """Creates a notification with pending status and correct fields."""
        user = await _create_user(db_session, telegram_id=83001)

        notification = await create_notification(
            type=NotificationType.BOOKING_CONFIRMED.value,
            title="Booking Confirmed",
            body="Your booking for Meditation 101 is confirmed.",
            target_type=TargetType.USER.value,
            target_value=str(user.id),
            session=db_session,
            action_data={
                "action": "open_booking",
                "params": {"booking_id": str(uuid4())},
            },
            priority=3,
        )

        assert notification.id is not None
        assert notification.status == NotificationStatus.PENDING.value
        assert notification.type == NotificationType.BOOKING_CONFIRMED.value
        assert notification.title == "Booking Confirmed"
        assert notification.target_type == TargetType.USER.value
        assert notification.target_value == str(user.id)
        assert notification.priority == 3
        assert notification.action_data["action"] == "open_booking"
        assert notification.scheduled_at is not None

    @pytest.mark.asyncio
    async def test_scheduled_at_defaults_to_now(
        self,
        db_session: AsyncSession,
        cleanup_notifications,
    ) -> None:
        """If scheduled_at is None, defaults to approximately now."""
        before = datetime.now(UTC)

        notification = await create_notification(
            type=NotificationType.SYSTEM_ANNOUNCEMENT.value,
            title="Test",
            body="Test body",
            target_type=TargetType.ALL.value,
            target_value="*",
            session=db_session,
        )

        after = datetime.now(UTC)
        assert before <= notification.scheduled_at <= after

    @pytest.mark.asyncio
    async def test_scheduled_at_in_future(
        self,
        db_session: AsyncSession,
        cleanup_notifications,
    ) -> None:
        """Can schedule a notification in the future."""
        future = datetime.now(UTC) + timedelta(hours=24)

        notification = await create_notification(
            type=NotificationType.REMINDER_24H.value,
            title="Reminder",
            body="Your practice is tomorrow.",
            target_type=TargetType.USER.value,
            target_value=str(uuid4()),
            session=db_session,
            scheduled_at=future,
        )

        assert notification.scheduled_at == future


# ===================================================================
# 2. Target resolution
# ===================================================================


class TestTargetResolution:
    """Tests for resolve_notification() target expansion."""

    @pytest.mark.asyncio
    async def test_user_target_single_delivery(
        self,
        db_session: AsyncSession,
        cleanup_notifications,
    ) -> None:
        """user target → exactly 1 delivery."""
        user = await _create_user(db_session, telegram_id=83010)

        notification = await create_notification(
            type=NotificationType.BOOKING_CONFIRMED.value,
            title="Confirmed",
            body="You're in!",
            target_type=TargetType.USER.value,
            target_value=str(user.id),
            session=db_session,
        )

        deliveries = await resolve_notification(
            notification, db_session,
        )

        assert len(deliveries) == 1
        assert deliveries[0].user_id == user.id
        assert deliveries[0].channel == DeliveryChannel.TELEGRAM.value
        assert deliveries[0].status == DeliveryStatus.PENDING.value

    @pytest.mark.asyncio
    async def test_user_target_nonexistent_user(
        self,
        db_session: AsyncSession,
        cleanup_notifications,
    ) -> None:
        """user target with nonexistent UUID → 0 deliveries."""
        notification = await create_notification(
            type=NotificationType.BOOKING_CONFIRMED.value,
            title="Confirmed",
            body="You're in!",
            target_type=TargetType.USER.value,
            target_value=str(uuid4()),
            session=db_session,
        )

        deliveries = await resolve_notification(
            notification, db_session,
        )

        assert len(deliveries) == 0

    @pytest.mark.asyncio
    async def test_practice_target_multiple_deliveries(
        self,
        db_session: AsyncSession,
        cleanup_notifications,
    ) -> None:
        """practice target → delivery for each booked user."""
        master = await _create_user(
            db_session, telegram_id=83020, role=UserRole.MASTER.value,
        )
        user1 = await _create_user(db_session, telegram_id=83021)
        user2 = await _create_user(db_session, telegram_id=83022)
        user3 = await _create_user(db_session, telegram_id=83023)

        # FK: practices.master_id -> master_profiles.user_id.
        master_profile = MasterProfile(user_id=master.id)
        db_session.add(master_profile)
        await db_session.flush()

        # Create a practice.
        practice = Practice(
            master_id=master.id,
            practice_type=PracticeType.LIVE.value,
            status=PracticeStatus.SCHEDULED.value,
            title="Meditation 101",
            scheduled_at=datetime.now(UTC) + timedelta(hours=2),
            duration_minutes=60,
            timezone="UTC",
            is_free=True,
            price_cents=0,
            currency="eur",
            current_participants=2,
        )
        db_session.add(practice)
        await db_session.flush()

        # Two confirmed bookings, one cancelled.
        for user, status in [
            (user1, BookingStatus.CONFIRMED.value),
            (user2, BookingStatus.CONFIRMED.value),
            (user3, BookingStatus.CANCELLED.value),
        ]:
            booking = Booking(
                practice_id=practice.id,
                user_id=user.id,
                status=status,
            )
            db_session.add(booking)
        await db_session.flush()

        notification = await create_notification(
            type=NotificationType.PRACTICE_CANCELLED.value,
            title="Practice Cancelled",
            body="Meditation 101 has been cancelled.",
            target_type=TargetType.PRACTICE.value,
            target_value=str(practice.id),
            session=db_session,
        )

        deliveries = await resolve_notification(
            notification, db_session,
        )

        # Only 2 deliveries (user1 + user2), not user3 (cancelled).
        assert len(deliveries) == 2
        delivery_user_ids = {d.user_id for d in deliveries}
        assert user1.id in delivery_user_ids
        assert user2.id in delivery_user_ids
        assert user3.id not in delivery_user_ids

    @pytest.mark.asyncio
    async def test_role_target(
        self,
        db_session: AsyncSession,
        cleanup_notifications,
    ) -> None:
        """role target → delivery for each user with that role."""
        master1 = await _create_user(
            db_session, telegram_id=83030, role=UserRole.MASTER.value,
        )
        master2 = await _create_user(
            db_session, telegram_id=83031, role=UserRole.MASTER.value,
        )
        # Regular user should NOT be included.
        _regular = await _create_user(
            db_session, telegram_id=83032, role=UserRole.USER.value,
        )

        notification = await create_notification(
            type=NotificationType.SYSTEM_ANNOUNCEMENT.value,
            title="New Feature",
            body="Check out the new dashboard.",
            target_type=TargetType.ROLE.value,
            target_value=UserRole.MASTER.value,
            session=db_session,
        )

        deliveries = await resolve_notification(
            notification, db_session,
        )

        delivery_user_ids = {d.user_id for d in deliveries}
        assert master1.id in delivery_user_ids
        assert master2.id in delivery_user_ids


# ===================================================================
# 3. Processor: Stage Resolve
# ===================================================================


class TestStageResolve:
    """Tests for _stage_resolve() processor stage."""

    @pytest.mark.asyncio
    async def test_resolves_due_notifications(
        self,
        db_session: AsyncSession,
        cleanup_notifications,
    ) -> None:
        """Pending notification with scheduled_at <= now gets resolved."""
        user = await _create_user(db_session, telegram_id=83040)

        await create_notification(
            type=NotificationType.BOOKING_CONFIRMED.value,
            title="Confirmed",
            body="Done.",
            target_type=TargetType.USER.value,
            target_value=str(user.id),
            session=db_session,
        )
        await db_session.commit()

        resolved = await _stage_resolve()
        assert resolved >= 1

        # Processor committed in its own session — reset test session.
        await db_session.rollback()

        # Verify deliveries were created.
        stmt = select(func.count(NotificationDelivery.id))
        count = (await db_session.execute(stmt)).scalar_one()
        assert count >= 1

    @pytest.mark.asyncio
    async def test_skips_future_notifications(
        self,
        db_session: AsyncSession,
        cleanup_notifications,
    ) -> None:
        """Notification scheduled in future is not resolved."""
        user = await _create_user(db_session, telegram_id=83041)

        await create_notification(
            type=NotificationType.REMINDER_24H.value,
            title="Reminder",
            body="Tomorrow.",
            target_type=TargetType.USER.value,
            target_value=str(user.id),
            session=db_session,
            scheduled_at=datetime.now(UTC) + timedelta(hours=24),
        )
        await db_session.commit()

        resolved = await _stage_resolve()
        assert resolved == 0

    @pytest.mark.asyncio
    async def test_expires_old_notifications(
        self,
        db_session: AsyncSession,
        cleanup_notifications,
    ) -> None:
        """Notification past expiry_at is marked expired, not resolved."""
        user = await _create_user(db_session, telegram_id=83042)

        notification = await create_notification(
            type=NotificationType.REMINDER_10MIN.value,
            title="Starting soon",
            body="10 minutes!",
            target_type=TargetType.USER.value,
            target_value=str(user.id),
            session=db_session,
            scheduled_at=datetime.now(UTC) - timedelta(hours=1),
            expiry_at=datetime.now(UTC) - timedelta(minutes=30),
        )
        nid = notification.id
        await db_session.commit()

        await _stage_resolve()

        # Processor committed in its own session — reset test session
        # to see changes.
        await db_session.rollback()

        # Refresh from a new query to see processor's changes.
        stmt = select(Notification).where(Notification.id == nid)
        result = await db_session.execute(stmt)
        refreshed = result.scalar_one()
        assert refreshed.status == NotificationStatus.EXPIRED.value


# ===================================================================
# 4. Processor: Stage Deliver
# ===================================================================


class TestStageDeliver:
    """Tests for _stage_deliver() processor stage."""

    @pytest.mark.asyncio
    async def test_stub_delivers_successfully(
        self,
        db_session: AsyncSession,
        cleanup_notifications,
    ) -> None:
        """StubFormatter sends successfully → delivery.status=sent."""
        user = await _create_user(db_session, telegram_id=83050)

        notification = await create_notification(
            type=NotificationType.BOOKING_CONFIRMED.value,
            title="Confirmed",
            body="Done.",
            target_type=TargetType.USER.value,
            target_value=str(user.id),
            session=db_session,
        )
        notification.status = NotificationStatus.PROCESSING.value

        deliveries = await resolve_notification(
            notification, db_session,
        )
        await db_session.commit()

        delivered = await _stage_deliver()
        assert delivered >= 1

        # Processor committed in its own session — reset test session.
        await db_session.rollback()

        # Check delivery status.
        stmt = select(NotificationDelivery).where(
            NotificationDelivery.notification_id == notification.id,
        )
        result = await db_session.execute(stmt)
        delivery = result.scalar_one()
        assert delivery.status == DeliveryStatus.SENT.value
        assert delivery.sent_at is not None
        assert delivery.attempts == 1

    @pytest.mark.asyncio
    async def test_failed_delivery_retries(
        self,
        db_session: AsyncSession,
        cleanup_notifications,
    ) -> None:
        """Failed send → attempts incremented, stays pending if under max."""
        user = await _create_user(db_session, telegram_id=83051)

        notification = await create_notification(
            type=NotificationType.BOOKING_CONFIRMED.value,
            title="Confirmed",
            body="Done.",
            target_type=TargetType.USER.value,
            target_value=str(user.id),
            session=db_session,
        )
        notification.status = NotificationStatus.PROCESSING.value
        await resolve_notification(notification, db_session)
        await db_session.commit()

        # Patch formatter to fail.
        fail_result = DeliveryResult(
            success=False, error_message="Connection timeout",
        )

        with patch(
            "app.modules.notifications.processor.get_formatter",
        ) as mock_get:
            mock_formatter = StubFormatter()

            async def _fail_send(**kwargs):
                return fail_result

            mock_formatter.send = _fail_send
            mock_get.return_value = mock_formatter

            await _stage_deliver()

        # Processor committed in its own session — reset test session.
        await db_session.rollback()

        # Delivery should still be pending (1 attempt < 3 max).
        stmt = select(NotificationDelivery).where(
            NotificationDelivery.notification_id == notification.id,
        )
        result = await db_session.execute(stmt)
        delivery = result.scalar_one()
        assert delivery.status == DeliveryStatus.PENDING.value
        assert delivery.attempts == 1
        assert delivery.error_message == "Connection timeout"

    @pytest.mark.asyncio
    async def test_max_attempts_marks_failed(
        self,
        db_session: AsyncSession,
        cleanup_notifications,
    ) -> None:
        """After max_attempts failures → delivery.status=failed."""
        user = await _create_user(db_session, telegram_id=83052)

        notification = await create_notification(
            type=NotificationType.BOOKING_CONFIRMED.value,
            title="Confirmed",
            body="Done.",
            target_type=TargetType.USER.value,
            target_value=str(user.id),
            session=db_session,
        )
        notification.status = NotificationStatus.PROCESSING.value
        await resolve_notification(notification, db_session)
        await db_session.commit()

        # Patch formatter to always fail.
        fail_result = DeliveryResult(
            success=False, error_message="API error",
        )

        with patch(
            "app.modules.notifications.processor.get_formatter",
        ) as mock_get:
            mock_formatter = StubFormatter()

            async def _fail_send(**kwargs):
                return fail_result

            mock_formatter.send = _fail_send
            mock_get.return_value = mock_formatter

            # Run deliver max_attempts times.
            max_att = settings.notification_max_delivery_attempts
            for _ in range(max_att):
                await _stage_deliver()

        # Processor committed in its own session — reset test session.
        await db_session.rollback()

        # Delivery should be failed.
        stmt = select(NotificationDelivery).where(
            NotificationDelivery.notification_id == notification.id,
        )
        result = await db_session.execute(stmt)
        delivery = result.scalar_one()
        assert delivery.status == DeliveryStatus.FAILED.value
        assert delivery.attempts == max_att


# ===================================================================
# 5. Processor: Rollup
# ===================================================================


class TestRollup:
    """Tests for _stage_rollup() notification status update."""

    @pytest.mark.asyncio
    async def test_all_sent_notification_becomes_sent(
        self,
        db_session: AsyncSession,
        cleanup_notifications,
    ) -> None:
        """When all deliveries are sent → notification.status=sent."""
        user = await _create_user(db_session, telegram_id=83060)

        notification = await create_notification(
            type=NotificationType.BOOKING_CONFIRMED.value,
            title="Confirmed",
            body="Done.",
            target_type=TargetType.USER.value,
            target_value=str(user.id),
            session=db_session,
        )
        notification.status = NotificationStatus.PROCESSING.value
        await resolve_notification(notification, db_session)
        await db_session.commit()

        # Deliver (stub succeeds).
        await _stage_deliver()

        # Rollup.
        await _stage_rollup()

        # Processor committed in its own session — reset test session.
        await db_session.rollback()

        stmt = select(Notification).where(
            Notification.id == notification.id,
        )
        result = await db_session.execute(stmt)
        refreshed = result.scalar_one()
        assert refreshed.status == NotificationStatus.SENT.value

    @pytest.mark.asyncio
    async def test_all_failed_notification_becomes_failed(
        self,
        db_session: AsyncSession,
        cleanup_notifications,
    ) -> None:
        """When all deliveries are failed → notification.status=failed."""
        user = await _create_user(db_session, telegram_id=83061)

        notification = await create_notification(
            type=NotificationType.BOOKING_CONFIRMED.value,
            title="Confirmed",
            body="Done.",
            target_type=TargetType.USER.value,
            target_value=str(user.id),
            session=db_session,
        )
        notification.status = NotificationStatus.PROCESSING.value
        await resolve_notification(notification, db_session)
        await db_session.commit()

        # Fail all attempts.
        fail_result = DeliveryResult(
            success=False, error_message="Dead",
        )
        with patch(
            "app.modules.notifications.processor.get_formatter",
        ) as mock_get:
            mock_formatter = StubFormatter()

            async def _fail_send(**kwargs):
                return fail_result

            mock_formatter.send = _fail_send
            mock_get.return_value = mock_formatter

            for _ in range(settings.notification_max_delivery_attempts):
                await _stage_deliver()

        # Rollup.
        await _stage_rollup()

        # Processor committed in its own session — reset test session.
        await db_session.rollback()

        stmt = select(Notification).where(
            Notification.id == notification.id,
        )
        result = await db_session.execute(stmt)
        refreshed = result.scalar_one()
        assert refreshed.status == NotificationStatus.FAILED.value
