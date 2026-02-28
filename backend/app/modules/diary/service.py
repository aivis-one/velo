# =============================================================================
# VELO Backend -- Diary Service (Phase 8.1: Check-ins, Phase 8.2: Feedbacks)
# =============================================================================
#
# UPSERT CHECKIN:
#   1. Find confirmed booking for (user, practice).
#   2. Validate time window: scheduled_at - checkin_window_hours .. scheduled_at.
#   3. Insert or update checkin (one per booking + check_type).
#   4. Audit log: checkin_created or checkin_updated.
#
# UPSERT FEEDBACK:
#   1. Find attended booking for (user, practice).
#   2. Validate practice is completed.
#   3. Validate time window: practice_end .. practice_end + feedback_window_hours.
#   4. Insert or update feedback (one per practice + user).
#   5. Audit log: feedback_created or feedback_updated.
#
# LIST CHECKINS / FEEDBACKS:
#   Paginated, filtered by practice_id, rating, and/or date range.
#   Read-only (get_db_reader in router).
#
# SESSION RULES:
#   No session.commit() here (P-01). Router manages transaction.
# =============================================================================

from datetime import UTC, datetime, timedelta
from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import record_audit
from app.core.config import settings
from app.core.exceptions import BadRequestError, NotFoundError
from app.modules.bookings.models import Booking, BookingStatus
from app.modules.diary.models import CheckType, Checkin, Feedback
from app.modules.practices.models import Practice, PracticeStatus
from app.modules.users.models import User

logger = structlog.get_logger()


# ===================================================================
# Upsert checkin (Phase 8.1)
# ===================================================================


async def upsert_checkin(
    user: User,
    practice_id: UUID,
    mood: str,
    session: AsyncSession,
    *,
    comment: str | None = None,
) -> tuple[Checkin, bool]:
    """Create or update a pre-practice check-in.

    Args:
        user: Authenticated user.
        practice_id: Target practice UUID.
        mood: One of low/mid/high.
        session: Write session (caller manages commit).
        comment: Optional text (max length validated in schema).

    Returns:
        Tuple of (checkin, is_new). is_new=True if created, False if updated.

    Raises:
        NotFoundError: No confirmed booking for this practice.
        BadRequestError: Outside check-in window.
    """
    # 1. Find confirmed booking for this user + practice.
    booking_stmt = (
        select(Booking)
        .where(
            Booking.practice_id == practice_id,
            Booking.user_id == user.id,
            Booking.status == BookingStatus.CONFIRMED.value,
        )
    )
    result = await session.execute(booking_stmt)
    booking = result.scalar_one_or_none()

    if booking is None:
        raise NotFoundError(
            "No confirmed booking found for this practice"
        )

    # 2. Load practice to check time window.
    practice = await session.get(Practice, practice_id)
    if practice is None:
        raise NotFoundError("Practice not found")

    _validate_checkin_window(practice)

    # 3. Check for existing checkin (upsert).
    existing_stmt = (
        select(Checkin)
        .where(
            Checkin.booking_id == booking.id,
            Checkin.check_type == CheckType.PRE.value,
        )
    )
    result = await session.execute(existing_stmt)
    existing = result.scalar_one_or_none()

    if existing is not None:
        # Update existing checkin.
        existing.mood = mood
        existing.comment = comment
        await session.flush()

        await record_audit(
            event="checkin_updated",
            actor_id=user.id,
            actor_type="user",
            target_type="checkin",
            target_id=existing.id,
            data={"mood": mood, "practice_id": str(practice_id)},
            session=session,
        )

        logger.info(
            "checkin_updated",
            checkin_id=str(existing.id),
            user_id=str(user.id),
            practice_id=str(practice_id),
            mood=mood,
        )
        return existing, False

    # 4. Create new checkin.
    checkin = Checkin(
        practice_id=practice_id,
        user_id=user.id,
        booking_id=booking.id,
        mood=mood,
        comment=comment,
        check_type=CheckType.PRE.value,
    )
    session.add(checkin)
    await session.flush()

    await record_audit(
        event="checkin_created",
        actor_id=user.id,
        actor_type="user",
        target_type="checkin",
        target_id=checkin.id,
        data={"mood": mood, "practice_id": str(practice_id)},
        session=session,
    )

    logger.info(
        "checkin_created",
        checkin_id=str(checkin.id),
        user_id=str(user.id),
        practice_id=str(practice_id),
        mood=mood,
    )
    return checkin, True


# ===================================================================
# List user checkins (Phase 8.1)
# ===================================================================


async def list_user_checkins(
    user: User,
    session: AsyncSession,
    *,
    limit: int = 20,
    offset: int = 0,
    practice_id: UUID | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> tuple[list[Checkin], int]:
    """List check-ins for a user with optional filters.

    Args:
        user: Authenticated user.
        session: Read session.
        limit: Page size.
        offset: Page offset.
        practice_id: Filter by practice.
        date_from: Filter by created_at >= date_from.
        date_to: Filter by created_at <= date_to.

    Returns:
        Tuple of (items, total_count).
    """
    base = select(Checkin).where(Checkin.user_id == user.id)
    count_base = select(func.count(Checkin.id)).where(
        Checkin.user_id == user.id,
    )

    if practice_id is not None:
        base = base.where(Checkin.practice_id == practice_id)
        count_base = count_base.where(
            Checkin.practice_id == practice_id,
        )

    if date_from is not None:
        base = base.where(Checkin.created_at >= date_from)
        count_base = count_base.where(Checkin.created_at >= date_from)

    if date_to is not None:
        base = base.where(Checkin.created_at <= date_to)
        count_base = count_base.where(Checkin.created_at <= date_to)

    # Total count.
    total = (await session.execute(count_base)).scalar_one()

    # Paginated items (newest first).
    items_stmt = (
        base
        .order_by(Checkin.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(items_stmt)
    items = list(result.scalars().all())

    return items, total


# ===================================================================
# Upsert feedback (Phase 8.2)
# ===================================================================


async def upsert_feedback(
    user: User,
    practice_id: UUID,
    rating: str,
    session: AsyncSession,
    *,
    comment: str | None = None,
) -> tuple[Feedback, bool]:
    """Create or update a post-practice feedback.

    Args:
        user: Authenticated user.
        practice_id: Target practice UUID.
        rating: One of fire/good/confused.
        session: Write session (caller manages commit).
        comment: Optional text (max length validated in schema).

    Returns:
        Tuple of (feedback, is_new). is_new=True if created, False if updated.

    Raises:
        NotFoundError: No attended booking for this practice.
        BadRequestError: Practice not completed or outside feedback window.
    """
    # 1. Find attended booking for this user + practice.
    booking_stmt = (
        select(Booking)
        .where(
            Booking.practice_id == practice_id,
            Booking.user_id == user.id,
            Booking.status == BookingStatus.ATTENDED.value,
        )
    )
    result = await session.execute(booking_stmt)
    booking = result.scalar_one_or_none()

    if booking is None:
        raise NotFoundError(
            "No attended booking found for this practice"
        )

    # 2. Load practice to check status and time window.
    practice = await session.get(Practice, practice_id)
    if practice is None:
        raise NotFoundError("Practice not found")

    _validate_feedback_window(practice)

    # 3. Check for existing feedback (upsert).
    existing_stmt = (
        select(Feedback)
        .where(
            Feedback.practice_id == practice_id,
            Feedback.user_id == user.id,
        )
    )
    result = await session.execute(existing_stmt)
    existing = result.scalar_one_or_none()

    if existing is not None:
        # Update existing feedback.
        existing.rating = rating
        existing.comment = comment
        await session.flush()

        await record_audit(
            event="feedback_updated",
            actor_id=user.id,
            actor_type="user",
            target_type="feedback",
            target_id=existing.id,
            data={"rating": rating, "practice_id": str(practice_id)},
            session=session,
        )

        logger.info(
            "feedback_updated",
            feedback_id=str(existing.id),
            user_id=str(user.id),
            practice_id=str(practice_id),
            rating=rating,
        )
        return existing, False

    # 4. Create new feedback.
    feedback = Feedback(
        practice_id=practice_id,
        user_id=user.id,
        booking_id=booking.id,
        rating=rating,
        comment=comment,
    )
    session.add(feedback)
    await session.flush()

    await record_audit(
        event="feedback_created",
        actor_id=user.id,
        actor_type="user",
        target_type="feedback",
        target_id=feedback.id,
        data={"rating": rating, "practice_id": str(practice_id)},
        session=session,
    )

    logger.info(
        "feedback_created",
        feedback_id=str(feedback.id),
        user_id=str(user.id),
        practice_id=str(practice_id),
        rating=rating,
    )
    return feedback, True


# ===================================================================
# List user feedbacks (Phase 8.2)
# ===================================================================


async def list_user_feedbacks(
    user: User,
    session: AsyncSession,
    *,
    limit: int = 20,
    offset: int = 0,
    practice_id: UUID | None = None,
    rating: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> tuple[list[Feedback], int]:
    """List feedbacks for a user with optional filters.

    Args:
        user: Authenticated user.
        session: Read session.
        limit: Page size.
        offset: Page offset.
        practice_id: Filter by practice.
        rating: Filter by rating value.
        date_from: Filter by created_at >= date_from.
        date_to: Filter by created_at <= date_to.

    Returns:
        Tuple of (items, total_count).
    """
    base = select(Feedback).where(Feedback.user_id == user.id)
    count_base = select(func.count(Feedback.id)).where(
        Feedback.user_id == user.id,
    )

    if practice_id is not None:
        base = base.where(Feedback.practice_id == practice_id)
        count_base = count_base.where(
            Feedback.practice_id == practice_id,
        )

    if rating is not None:
        base = base.where(Feedback.rating == rating)
        count_base = count_base.where(Feedback.rating == rating)

    if date_from is not None:
        base = base.where(Feedback.created_at >= date_from)
        count_base = count_base.where(Feedback.created_at >= date_from)

    if date_to is not None:
        base = base.where(Feedback.created_at <= date_to)
        count_base = count_base.where(Feedback.created_at <= date_to)

    # Total count.
    total = (await session.execute(count_base)).scalar_one()

    # Paginated items (newest first).
    items_stmt = (
        base
        .order_by(Feedback.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(items_stmt)
    items = list(result.scalars().all())

    return items, total


# ===================================================================
# Helpers
# ===================================================================


def _validate_checkin_window(practice: Practice) -> None:
    """Validate that current time is within the check-in window.

    Window: [scheduled_at - checkin_window_hours, scheduled_at].

    Raises:
        BadRequestError: If outside the window.
    """
    now = datetime.now(UTC)
    window_hours = settings.checkin_window_hours
    window_start = practice.scheduled_at - timedelta(hours=window_hours)
    window_end = practice.scheduled_at

    if now < window_start:
        raise BadRequestError(
            f"Check-in window opens {window_hours} hours before the practice"
        )

    if now > window_end:
        raise BadRequestError(
            "Check-in window has closed (practice has started)"
        )


def _validate_feedback_window(practice: Practice) -> None:
    """Validate that practice is completed and within feedback window.

    Precondition: practice.status == completed.
    Window: [practice_end, practice_end + feedback_window_hours].
    Where practice_end = scheduled_at + duration_minutes.

    Raises:
        BadRequestError: If practice not completed or outside window.
    """
    if practice.status != PracticeStatus.COMPLETED.value:
        raise BadRequestError(
            "Feedback can only be submitted for completed practices"
        )

    now = datetime.now(UTC)
    window_hours = settings.feedback_window_hours
    practice_end = practice.scheduled_at + timedelta(
        minutes=practice.duration_minutes,
    )
    window_close = practice_end + timedelta(hours=window_hours)

    if now > window_close:
        raise BadRequestError(
            "Feedback window has closed "
            f"({window_hours} hours after practice ended)"
        )
