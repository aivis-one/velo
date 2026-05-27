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
# 11.1 fix: list_user_checkins / list_user_feedbacks / list_user_diary_entries
#   previously built two parallel queries (base + count_base) and applied
#   every filter clause twice. Now count is derived from the base query as a
#   subquery: select(func.count()).select_from(base.subquery()). Filters are
#   applied once; count_base duplication is eliminated.
#
# SESSION RULES:
#   No session.commit() here (P-01). Router manages transaction.
# =============================================================================

from datetime import UTC, datetime, timedelta
from uuid import UUID

import structlog
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import record_audit
from app.core.config import settings
from app.core.exceptions import BadRequestError, NotFoundError
from app.modules.bookings.models import Booking, BookingStatus
from app.modules.diary.models import (
    CheckType,
    Checkin,
    DiaryEntry,
    DiaryEntryType,
    DiaryEvent,
    Feedback,
)
from app.modules.diary.projections import (
    hide_entry_event,
    upsert_checkin_event,
    upsert_entry_event,
    upsert_feedback_event,
)
from app.modules.masters.service import get_master_display_name
from app.modules.practices.models import Practice, PracticeStatus
from app.modules.users.models import User

logger = structlog.get_logger()


# ===================================================================
# Upsert checkin (Phase 8.1)
# ===================================================================


async def upsert_checkin(
    user: User,
    practice_id: UUID,
    mood: int,
    session: AsyncSession,
    *,
    comment: str | None = None,
) -> tuple[Checkin, bool]:
    """Create or update a pre-practice check-in.

    Args:
        user: Authenticated user.
        practice_id: Target practice UUID.
        mood: A 1..10 score (validated in schema).
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

    now = datetime.now(UTC)
    window_open = practice.scheduled_at - timedelta(
        hours=settings.checkin_window_hours,
    )

    if now < window_open:
        raise BadRequestError(
            f"Check-in window opens "
            f"{settings.checkin_window_hours}h before the practice"
        )
    if now >= practice.scheduled_at:
        raise BadRequestError("Check-in window has closed")

    # 3. Upsert.
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
        # Update.
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

        # Diary feed: refresh the timeline event for this check-in.
        master_name = await get_master_display_name(practice.master_id, session)
        await upsert_checkin_event(
            session,
            checkin=existing,
            practice=practice,
            master_name=master_name,
        )
        return existing, False

    # Create new checkin.
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

    # Diary feed: project the new check-in onto the user's timeline.
    master_name = await get_master_display_name(practice.master_id, session)
    await upsert_checkin_event(
        session,
        checkin=checkin,
        practice=practice,
        master_name=master_name,
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

    11.1 fix: total count derived from base query subquery instead of
    maintaining a parallel count_base with duplicated filter clauses.

    Returns:
        Tuple of (items, total_count).
    """
    base = select(Checkin).where(Checkin.user_id == user.id)

    if practice_id is not None:
        base = base.where(Checkin.practice_id == practice_id)

    if date_from is not None:
        base = base.where(Checkin.created_at >= date_from)

    if date_to is not None:
        base = base.where(Checkin.created_at <= date_to)

    # Count via subquery -- filters applied once.
    total = (
        await session.execute(
            select(func.count()).select_from(base.subquery())
        )
    ).scalar_one()

    items_stmt = (
        base
        .order_by(Checkin.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(items_stmt)
    items = list(result.scalars().all())

    return items, total


async def get_checkin(
    user: User,
    checkin_id: UUID,
    session: AsyncSession,
) -> Checkin:
    """Get a single check-in owned by the user (read-only detail).

    Raises:
        NotFoundError: Check-in not found or not owned by user.
    """
    checkin = await session.get(Checkin, checkin_id)

    if checkin is None or checkin.user_id != user.id:
        raise NotFoundError("Check-in not found")

    return checkin


# ===================================================================
# Upsert feedback (Phase 8.2)
# ===================================================================


async def upsert_feedback(
    user: User,
    practice_id: UUID,
    rating: int,
    session: AsyncSession,
    *,
    comment: str | None = None,
) -> tuple[Feedback, bool]:
    """Create or update a post-practice feedback.

    Args:
        user: Authenticated user.
        practice_id: Target practice UUID.
        rating: A 1..10 score (validated in schema).
        session: Write session (caller manages commit).
        comment: Optional text (max length validated in schema).

    Returns:
        Tuple of (feedback, is_new).

    Raises:
        NotFoundError: No attended booking for this practice.
        BadRequestError: Practice not completed or outside feedback window.
    """
    # 1. Find attended booking.
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

    # 2. Load practice to check window.
    practice = await session.get(Practice, practice_id)
    if practice is None:
        raise NotFoundError("Practice not found")

    if practice.status != PracticeStatus.COMPLETED.value:
        raise BadRequestError("Feedback is only available after practice completion")

    now = datetime.now(UTC)
    window_close = practice.scheduled_at + timedelta(
        minutes=practice.duration_minutes,
        hours=settings.feedback_window_hours,
    )

    if now > window_close:
        raise BadRequestError("Feedback window has closed")

    # 3. Upsert.
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

        # Diary feed: refresh the timeline event for this feedback.
        master_name = await get_master_display_name(practice.master_id, session)
        await upsert_feedback_event(
            session,
            feedback=existing,
            practice=practice,
            master_name=master_name,
        )
        return existing, False

    # Create new feedback.
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

    # Diary feed: project the new feedback onto the user's timeline.
    master_name = await get_master_display_name(practice.master_id, session)
    await upsert_feedback_event(
        session,
        feedback=feedback,
        practice=practice,
        master_name=master_name,
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
    rating: int | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> tuple[list[Feedback], int]:
    """List feedbacks for a user with optional filters.

    11.1 fix: count derived from base subquery.

    Returns:
        Tuple of (items, total_count).
    """
    base = select(Feedback).where(Feedback.user_id == user.id)

    if practice_id is not None:
        base = base.where(Feedback.practice_id == practice_id)

    if rating is not None:
        base = base.where(Feedback.rating == rating)

    if date_from is not None:
        base = base.where(Feedback.created_at >= date_from)

    if date_to is not None:
        base = base.where(Feedback.created_at <= date_to)

    total = (
        await session.execute(
            select(func.count()).select_from(base.subquery())
        )
    ).scalar_one()

    items_stmt = (
        base
        .order_by(Feedback.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(items_stmt)
    items = list(result.scalars().all())

    return items, total


async def get_feedback(
    user: User,
    feedback_id: UUID,
    session: AsyncSession,
) -> Feedback:
    """Get a single feedback owned by the user (read-only detail).

    Raises:
        NotFoundError: Feedback not found or not owned by user.
    """
    feedback = await session.get(Feedback, feedback_id)

    if feedback is None or feedback.user_id != user.id:
        raise NotFoundError("Feedback not found")

    return feedback


# ===================================================================
# Create diary entry (Phase 8.3)
# ===================================================================


async def create_diary_entry(
    user: User,
    content: str,
    session: AsyncSession,
    *,
    title: str | None = None,
    mood: int | None = None,
    practice_id: UUID | None = None,
    entry_type: str = DiaryEntryType.NOTE.value,
    practice_phase: str | None = None,
) -> DiaryEntry:
    """Create a personal diary entry.

    Args:
        user: Authenticated user.
        content: Entry text (1-10000 chars, validated in schema).
        session: Write session (caller manages commit).
        title: Optional short title (max 200 chars).
        mood: Optional 1..10 score (validated in schema).
        practice_id: Optional practice link. Validated if provided.
        entry_type: note (free-form) or dream (Сонник). Defaults to note --
            the ledger composer only creates note this iteration.
        practice_phase: before/after relative to the linked practice; only
            meaningful when practice_id is set.

    Returns:
        Created DiaryEntry.

    Raises:
        NotFoundError: practice_id invalid or user has no booking.
    """
    if practice_id is not None:
        await _validate_practice_link(user.id, practice_id, session)

    entry = DiaryEntry(
        user_id=user.id,
        content=content,
        title=title,
        mood=mood,
        practice_id=practice_id,
        entry_type=entry_type,
        practice_phase=practice_phase,
    )
    session.add(entry)
    await session.flush()

    await record_audit(
        event="diary_entry_created",
        actor_id=user.id,
        actor_type="user",
        target_type="diary_entry",
        target_id=entry.id,
        data={
            "practice_id": str(practice_id) if practice_id else None,
            "entry_type": entry_type,
        },
        session=session,
    )

    logger.info(
        "diary_entry_created",
        entry_id=str(entry.id),
        user_id=str(user.id),
        entry_type=entry_type,
        mood=mood,
    )

    # Diary feed: project the new entry onto the user's timeline.
    await upsert_entry_event(session, entry=entry)
    return entry


async def _validate_practice_link(
    user_id: UUID,
    practice_id: UUID,
    session: AsyncSession,
) -> None:
    """Validate that practice exists and user has any booking for it.

    Raises:
        NotFoundError: Practice not found or user has no booking.
    """
    practice = await session.get(Practice, practice_id)
    if practice is None:
        raise NotFoundError("Practice not found")

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
        raise BadRequestError("Cannot link diary entry to a practice without a booking")


# ===================================================================
# Get diary entry (Phase 8.3)
# ===================================================================


async def get_diary_entry(
    user: User,
    entry_id: UUID,
    session: AsyncSession,
) -> DiaryEntry:
    """Get a single diary entry owned by the user.

    Raises:
        NotFoundError: Entry not found or not owned by user.
    """
    entry = await session.get(DiaryEntry, entry_id)

    if entry is None or entry.user_id != user.id or entry.is_deleted:
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
    mood: int | None = None,
    practice_id: UUID | None = None,
    entry_type: str | None = None,
    practice_phase: str | None = None,
    clear_title: bool = False,
    clear_mood: bool = False,
    clear_practice: bool = False,
    clear_practice_phase: bool = False,
) -> DiaryEntry:
    """Partially update a diary entry.

    Only provided fields are updated. Use clear_* flags to set
    nullable fields to None.

    Raises:
        NotFoundError: Entry not found, not owned by user, or soft-deleted.
        BadRequestError: New practice_id invalid.
    """
    entry = await session.get(DiaryEntry, entry_id)

    if entry is None or entry.user_id != user.id or entry.is_deleted:
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

    if entry_type is not None:
        entry.entry_type = entry_type

    if practice_phase is not None:
        entry.practice_phase = practice_phase
    elif clear_practice_phase:
        entry.practice_phase = None

    await session.flush()

    await record_audit(
        event="diary_entry_updated",
        actor_id=user.id,
        actor_type="user",
        target_type="diary_entry",
        target_id=entry.id,
        data={
            "practice_id": str(entry.practice_id) if entry.practice_id else None,
            "entry_type": entry.entry_type,
        },
        session=session,
    )

    logger.info(
        "diary_entry_updated",
        entry_id=str(entry.id),
        user_id=str(user.id),
    )

    # Diary feed: refresh the timeline event (snapshot + kind + text).
    await upsert_entry_event(session, entry=entry)
    return entry


# ===================================================================
# Delete diary entry (Phase 8.3)
# ===================================================================


async def delete_diary_entry(
    user: User,
    entry_id: UUID,
    session: AsyncSession,
) -> None:
    """Soft-delete a diary entry owned by the user.

    Redesign: this is a SOFT delete -- the row is hidden (is_deleted=True),
    not physically removed. The matching DiaryEvent is hidden in parallel
    (is_hidden=True) so it drops out of the feed while staying a stable
    target for future relations. Personal data remains recoverable.

    Raises:
        NotFoundError: Entry not found, not owned by user, or already deleted.
    """
    entry = await session.get(DiaryEntry, entry_id)

    if entry is None or entry.user_id != user.id or entry.is_deleted:
        raise NotFoundError("Diary entry not found")

    entry.is_deleted = True
    await session.flush()

    await record_audit(
        event="diary_entry_deleted",
        actor_id=user.id,
        actor_type="user",
        target_type="diary_entry",
        target_id=entry.id,
        data={"title": entry.title},
        session=session,
    )

    # Diary feed: hide the timeline event (soft) -- never drop the row.
    await hide_entry_event(session, entry_id=entry.id)

    logger.info(
        "diary_entry_deleted",
        entry_id=str(entry_id),
        user_id=str(user.id),
    )


# ===================================================================
# Restore diary entry (Diary redesign -- undo soft-delete)
# ===================================================================


async def restore_diary_entry(
    user: User,
    entry_id: UUID,
    session: AsyncSession,
) -> DiaryEntry:
    """Restore a soft-deleted diary entry owned by the user (undo delete).

    Mirror of delete_diary_entry: clears is_deleted and re-projects the
    timeline event (upsert_entry_event sets is_hidden = entry.is_deleted, so
    re-projecting un-hides it and the entry returns to the feed).

    We load the row directly (NOT via get_diary_entry, which 404s deleted
    rows) and require it to be currently deleted -- restoring an active entry
    is a no-op the client never needs, so we 404 to keep the contract tight.

    Raises:
        NotFoundError: Entry not found, not owned by user, or not deleted.
    """
    entry = await session.get(DiaryEntry, entry_id)

    if entry is None or entry.user_id != user.id or not entry.is_deleted:
        raise NotFoundError("Diary entry not found")

    entry.is_deleted = False
    await session.flush()

    await record_audit(
        event="diary_entry_restored",
        actor_id=user.id,
        actor_type="user",
        target_type="diary_entry",
        target_id=entry.id,
        data={"title": entry.title},
        session=session,
    )

    # Diary feed: re-project the timeline event -- upsert sets is_hidden to
    # entry.is_deleted (now False), so the event reappears in the feed.
    await upsert_entry_event(session, entry=entry)

    logger.info(
        "diary_entry_restored",
        entry_id=str(entry_id),
        user_id=str(user.id),
    )
    return entry


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
    mood: int | None = None,
    entry_type: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> tuple[list[DiaryEntry], int]:
    """List diary entries for a user with optional filters.

    11.1 fix: count derived from base subquery.
    Redesign: soft-deleted entries (is_deleted=True) are excluded.

    Returns:
        Tuple of (items, total_count).
    """
    base = select(DiaryEntry).where(
        DiaryEntry.user_id == user.id,
        DiaryEntry.is_deleted.is_(False),
    )

    if practice_id is not None:
        base = base.where(DiaryEntry.practice_id == practice_id)

    if mood is not None:
        base = base.where(DiaryEntry.mood == mood)

    if entry_type is not None:
        base = base.where(DiaryEntry.entry_type == entry_type)

    if date_from is not None:
        base = base.where(DiaryEntry.created_at >= date_from)

    if date_to is not None:
        base = base.where(DiaryEntry.created_at <= date_to)

    total = (
        await session.execute(
            select(func.count()).select_from(base.subquery())
        )
    ).scalar_one()

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
# Diary feed (Diary redesign iteration -- unified timeline)
# ===================================================================


def _kinds_for_categories(categories: list[str] | None) -> list[str] | None:
    """Resolve filter-chip categories to the set of event kinds they include.

    None / empty -> None (no kind filter -> "Все"). Unknown categories are
    ignored. Categories map to kinds via settings.diary_feed_categories
    (NO-LITERALS). Multiple categories union their kinds.
    """
    if not categories:
        return None
    mapping = settings.diary_feed_categories
    kinds: list[str] = []
    for category in categories:
        kinds.extend(mapping.get(category, []))
    # De-dup while preserving order; empty result means no valid category was
    # passed -> treat as no filter rather than "match nothing".
    deduped = list(dict.fromkeys(kinds))
    return deduped or None


async def list_diary_feed(
    user: User,
    session: AsyncSession,
    *,
    limit: int = 20,
    cursor: datetime | None = None,
    categories: list[str] | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    search: str | None = None,
) -> tuple[list[DiaryEvent], datetime | None]:
    """List the unified diary timeline for a user (cursor-paginated).

    The feed reads the append-only DiaryEvent journal in one query, newest
    first. Hidden events (soft-deleted entries) are excluded.

    Filters:
        categories: filter chips (entries/dreams/feedbacks/checkins/
            practices) -> resolved to event kinds. None -> all.
        date_from / date_to: bound occurred_at.
        search: case-insensitive ilike over the denormalized text_search.
        cursor: occurred_at of the last item from the previous page; the
            next page returns events strictly OLDER than the cursor.

    Returns:
        Tuple of (events, next_cursor). next_cursor is the occurred_at of the
        last returned event when a full page was returned, else None (end of
        feed). The caller echoes it back as `cursor` for the next page.

    Note on cursor stability: occurred_at is not guaranteed unique across
    events (a master fan-out stamps many rows with the same instant). For
    alpha volumes a plain occurred_at cursor is acceptable; a future tie-break
    (occurred_at, id) can be added without an API change.
    """
    base = select(DiaryEvent).where(
        DiaryEvent.user_id == user.id,
        DiaryEvent.is_hidden.is_(False),
    )

    kinds = _kinds_for_categories(categories)
    if kinds is not None:
        base = base.where(DiaryEvent.kind.in_(kinds))

    if date_from is not None:
        base = base.where(DiaryEvent.occurred_at >= date_from)

    if date_to is not None:
        base = base.where(DiaryEvent.occurred_at <= date_to)

    if search:
        # text_search is stored lowercased; lower the needle to match.
        needle = f"%{search.lower()}%"
        base = base.where(
            or_(
                DiaryEvent.text_search.ilike(needle),
                # Practice title lives in the snapshot for practice cards
                # that may have an empty text_search; match it too.
                DiaryEvent.snapshot["practice_title"].as_string().ilike(needle),
            )
        )

    if cursor is not None:
        base = base.where(DiaryEvent.occurred_at < cursor)

    stmt = (
        base
        .order_by(DiaryEvent.occurred_at.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    items = list(result.scalars().all())

    # next_cursor only when the page was full (more may remain).
    next_cursor = (
        items[-1].occurred_at if len(items) == limit else None
    )
    return items, next_cursor


# ===================================================================
# Practice insights (Phase 8.4, master-facing)
# ===================================================================


def _score_bucket(score: int) -> str:
    """Map a 1..10 mood/rating score into a distribution bucket.

    1-3 -> low, 4-7 -> mid, 8-10 -> high. Feedback ratings reuse the same
    ranges under different names (confused/good/fire) via a name map at the
    call site.
    """
    if score <= 3:
        return "low"
    if score <= 7:
        return "mid"
    return "high"


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
    from app.modules.bookings.models import Booking, BookingStatus
    participants_stmt = (
        select(func.count(Booking.id))
        .where(
            Booking.practice_id == practice_id,
            Booking.status == BookingStatus.ATTENDED.value,
        )
    )
    participants = (await session.execute(participants_stmt)).scalar_one()

    # 3. Mood distribution from check-ins, bucketed by score range
    #    (1-3 low / 4-7 mid / 8-10 high). mood is a 1..10 score now, so we
    #    pull the scores and bucket in Python rather than GROUP BY a string.
    checkins_stmt = (
        select(Checkin.mood, func.count(Checkin.id))
        .where(Checkin.practice_id == practice_id)
        .group_by(Checkin.mood)
    )
    checkins_result = await session.execute(checkins_stmt)
    checkins_buckets = {"low": 0, "mid": 0, "high": 0}
    for score, count in checkins_result.all():
        checkins_buckets[_score_bucket(score)] += count

    # 4. Rating distribution from feedbacks, bucketed by the same ranges
    #    (1-3 confused / 4-7 good / 8-10 fire).
    feedbacks_stmt = (
        select(Feedback.rating, func.count(Feedback.id))
        .where(Feedback.practice_id == practice_id)
        .group_by(Feedback.rating)
    )
    feedbacks_result = await session.execute(feedbacks_stmt)
    feedbacks_buckets = {"confused": 0, "good": 0, "fire": 0}
    _rating_bucket_name = {"low": "confused", "mid": "good", "high": "fire"}
    for score, count in feedbacks_result.all():
        feedbacks_buckets[_rating_bucket_name[_score_bucket(score)]] += count

    # 5. Count feedbacks with comments.
    comments_stmt = (
        select(func.count(Feedback.id))
        .where(
            Feedback.practice_id == practice_id,
            Feedback.comment.isnot(None),
        )
    )
    comments_count = (await session.execute(comments_stmt)).scalar_one()

    # MoodDistribution / RatingDistribution fields are required; the buckets
    # above are pre-seeded with all keys at 0, so missing scores are covered.
    return {
        "practice_id": practice_id,
        "participants": participants,
        "checkins": {
            "high": checkins_buckets["high"],
            "mid": checkins_buckets["mid"],
            "low": checkins_buckets["low"],
        },
        "feedbacks": {
            "fire": feedbacks_buckets["fire"],
            "good": feedbacks_buckets["good"],
            "confused": feedbacks_buckets["confused"],
        },
        "comments_count": comments_count,
    }
