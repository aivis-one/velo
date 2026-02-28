# =============================================================================
# VELO Backend -- Diary Service (Phase 8.1-8.4)
# =============================================================================
#
# UPSERT CHECKIN (8.1):
#   Find confirmed booking → validate window → insert or update.
#
# UPSERT FEEDBACK (8.2):
#   Find attended booking → validate completed + window → insert or update.
#
# DIARY ENTRY CRUD (8.3):
#   Create / get / update / delete / list.
#   If practice_id provided: validate practice exists + user has booking.
#
# PRACTICE INSIGHTS (8.4, master-facing):
#   Aggregated mood/rating distributions + participants + comments count.
#   Anonymous: no user IDs, names, or comment texts.
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
from app.modules.diary.models import CheckType, Checkin, DiaryEntry, Feedback
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

    total = (await session.execute(count_base)).scalar_one()

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

    total = (await session.execute(count_base)).scalar_one()

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
# Create diary entry (Phase 8.3)
# ===================================================================


async def create_diary_entry(
    user: User,
    content: str,
    session: AsyncSession,
    *,
    title: str | None = None,
    mood: str | None = None,
    practice_id: UUID | None = None,
) -> DiaryEntry:
    """Create a personal diary entry.

    Args:
        user: Authenticated user.
        content: Entry text (1-10000 chars, validated in schema).
        session: Write session.
        title: Optional title (max 200 chars).
        mood: Optional mood (low/mid/high).
        practice_id: Optional link to a practice.

    Returns:
        Created DiaryEntry.

    Raises:
        NotFoundError: practice_id provided but practice not found.
        BadRequestError: practice_id provided but user has no booking.
    """
    if practice_id is not None:
        await _validate_practice_link(user.id, practice_id, session)

    entry = DiaryEntry(
        user_id=user.id,
        practice_id=practice_id,
        title=title,
        content=content,
        mood=mood,
    )
    session.add(entry)
    await session.flush()

    await record_audit(
        event="diary_entry_created",
        actor_id=user.id,
        actor_type="user",
        target_type="diary_entry",
        target_id=entry.id,
        data={"practice_id": str(practice_id) if practice_id else None},
        session=session,
    )

    logger.info(
        "diary_entry_created",
        entry_id=str(entry.id),
        user_id=str(user.id),
        practice_id=str(practice_id) if practice_id else None,
    )
    return entry


# ===================================================================
# Get single diary entry (Phase 8.3)
# ===================================================================


async def get_diary_entry(
    user: User,
    entry_id: UUID,
    session: AsyncSession,
) -> DiaryEntry:
    """Get a single diary entry owned by the user.

    Raises:
        NotFoundError: Entry not found or not owned by user (P-08).
    """
    entry = await session.get(DiaryEntry, entry_id)

    if entry is None or entry.user_id != user.id:
        raise NotFoundError("Diary entry not found")

    return entry


# ===================================================================
# Update diary entry (Phase 8.3)
# ===================================================================


async def update_diary_entry(
    user: User,
    entry_id: UUID,
    session: AsyncSession,
    *,
    content: str | None = None,
    title: str | None = None,
    mood: str | None = None,
    practice_id: UUID | None = None,
    clear_mood: bool = False,
    clear_title: bool = False,
    clear_practice: bool = False,
) -> DiaryEntry:
    """Update a diary entry owned by the user.

    Only provided fields are updated. Use clear_* flags to set
    nullable fields to None.

    Raises:
        NotFoundError: Entry not found or not owned by user.
        BadRequestError: New practice_id invalid.
    """
    entry = await session.get(DiaryEntry, entry_id)

    if entry is None or entry.user_id != user.id:
        raise NotFoundError("Diary entry not found")

    # Validate new practice link if provided.
    if practice_id is not None:
        await _validate_practice_link(user.id, practice_id, session)
        entry.practice_id = practice_id
    elif clear_practice:
        entry.practice_id = None

    if content is not None:
        entry.content = content

    if title is not None:
        entry.title = title
    elif clear_title:
        entry.title = None

    if mood is not None:
        entry.mood = mood
    elif clear_mood:
        entry.mood = None

    await session.flush()

    await record_audit(
        event="diary_entry_updated",
        actor_id=user.id,
        actor_type="user",
        target_type="diary_entry",
        target_id=entry.id,
        data={"practice_id": str(entry.practice_id) if entry.practice_id else None},
        session=session,
    )

    logger.info(
        "diary_entry_updated",
        entry_id=str(entry.id),
        user_id=str(user.id),
    )
    return entry


# ===================================================================
# Delete diary entry (Phase 8.3)
# ===================================================================


async def delete_diary_entry(
    user: User,
    entry_id: UUID,
    session: AsyncSession,
) -> None:
    """Hard-delete a diary entry owned by the user.

    Raises:
        NotFoundError: Entry not found or not owned by user.
    """
    entry = await session.get(DiaryEntry, entry_id)

    if entry is None or entry.user_id != user.id:
        raise NotFoundError("Diary entry not found")

    await record_audit(
        event="diary_entry_deleted",
        actor_id=user.id,
        actor_type="user",
        target_type="diary_entry",
        target_id=entry.id,
        data={"title": entry.title},
        session=session,
    )

    await session.delete(entry)
    await session.flush()

    logger.info(
        "diary_entry_deleted",
        entry_id=str(entry_id),
        user_id=str(user.id),
    )


# ===================================================================
# List user diary entries (Phase 8.3)
# ===================================================================


async def list_user_diary_entries(
    user: User,
    session: AsyncSession,
    *,
    limit: int = 20,
    offset: int = 0,
    practice_id: UUID | None = None,
    mood: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> tuple[list[DiaryEntry], int]:
    """List diary entries for a user with optional filters.

    Returns:
        Tuple of (items, total_count).
    """
    base = select(DiaryEntry).where(DiaryEntry.user_id == user.id)
    count_base = select(func.count(DiaryEntry.id)).where(
        DiaryEntry.user_id == user.id,
    )

    if practice_id is not None:
        base = base.where(DiaryEntry.practice_id == practice_id)
        count_base = count_base.where(
            DiaryEntry.practice_id == practice_id,
        )

    if mood is not None:
        base = base.where(DiaryEntry.mood == mood)
        count_base = count_base.where(DiaryEntry.mood == mood)

    if date_from is not None:
        base = base.where(DiaryEntry.created_at >= date_from)
        count_base = count_base.where(DiaryEntry.created_at >= date_from)

    if date_to is not None:
        base = base.where(DiaryEntry.created_at <= date_to)
        count_base = count_base.where(DiaryEntry.created_at <= date_to)

    total = (await session.execute(count_base)).scalar_one()

    items_stmt = (
        base
        .order_by(DiaryEntry.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(items_stmt)
    items = list(result.scalars().all())

    return items, total


# ===================================================================
# Practice insights (Phase 8.4, master-facing)
# ===================================================================


async def get_practice_insights(
    user: User,
    practice_id: UUID,
    session: AsyncSession,
) -> dict:
    """Get aggregated anonymous insights for a completed practice.

    Only the practice's master can access insights.

    Args:
        user: Authenticated user (must be practice owner).
        practice_id: Target practice UUID.
        session: Read session.

    Returns:
        Dict with participants, checkins distribution, feedbacks
        distribution, and comments_count.

    Raises:
        NotFoundError: Practice not found or user is not the owner (P-08).
        BadRequestError: Practice is not completed.
    """
    # 1. Load practice and verify ownership.
    practice = await session.get(Practice, practice_id)

    if practice is None or practice.master_id != user.id:
        raise NotFoundError("Practice not found")

    if practice.status != PracticeStatus.COMPLETED.value:
        raise BadRequestError(
            "Insights are only available for completed practices"
        )

    # 2. Count attended participants.
    participants_stmt = (
        select(func.count(Booking.id))
        .where(
            Booking.practice_id == practice_id,
            Booking.status == BookingStatus.ATTENDED.value,
        )
    )
    participants = (await session.execute(participants_stmt)).scalar_one()

    # 3. Mood distribution from check-ins.
    mood_stmt = (
        select(Checkin.mood, func.count(Checkin.id))
        .where(Checkin.practice_id == practice_id)
        .group_by(Checkin.mood)
    )
    mood_rows = (await session.execute(mood_stmt)).all()
    mood_dist = {"high": 0, "mid": 0, "low": 0}
    for mood_val, cnt in mood_rows:
        if mood_val in mood_dist:
            mood_dist[mood_val] = cnt

    # 4. Rating distribution from feedbacks.
    rating_stmt = (
        select(Feedback.rating, func.count(Feedback.id))
        .where(Feedback.practice_id == practice_id)
        .group_by(Feedback.rating)
    )
    rating_rows = (await session.execute(rating_stmt)).all()
    rating_dist = {"fire": 0, "good": 0, "confused": 0}
    for rating_val, cnt in rating_rows:
        if rating_val in rating_dist:
            rating_dist[rating_val] = cnt

    # 5. Count non-null feedback comments.
    comments_stmt = (
        select(func.count(Feedback.id))
        .where(
            Feedback.practice_id == practice_id,
            Feedback.comment.isnot(None),
        )
    )
    comments_count = (await session.execute(comments_stmt)).scalar_one()

    return {
        "practice_id": practice_id,
        "participants": participants,
        "checkins": mood_dist,
        "feedbacks": rating_dist,
        "comments_count": comments_count,
    }


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


async def _validate_practice_link(
    user_id: UUID,
    practice_id: UUID,
    session: AsyncSession,
) -> None:
    """Validate that practice exists and user has a booking for it.

    Raises:
        NotFoundError: Practice does not exist.
        BadRequestError: User has no booking for this practice.
    """
    practice = await session.get(Practice, practice_id)
    if practice is None:
        raise NotFoundError("Practice not found")

    # Check user has any non-cancelled booking.
    booking_stmt = (
        select(func.count(Booking.id))
        .where(
            Booking.practice_id == practice_id,
            Booking.user_id == user_id,
            Booking.status != BookingStatus.CANCELLED.value,
        )
    )
    count = (await session.execute(booking_stmt)).scalar_one()

    if count == 0:
        raise BadRequestError(
            "Cannot link diary entry to a practice without a booking"
        )
