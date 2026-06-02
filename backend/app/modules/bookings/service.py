# =============================================================================
# VELO Backend -- Booking Service (Phase 5.1+5.2+5.3+5.4+6.5+6.7, Backlog)
# =============================================================================
#
# Business logic for booking create, cancel, attendance, finalize,
# and user-facing list/detail endpoints (Frontend Backlog).
#
# STATE MACHINE:
#   pending   -> confirmed, cancelled
#   confirmed -> attended, no_show, cancelled
#   attended  -> (terminal)
#   no_show   -> (terminal)
#   cancelled -> (terminal)
#
# ATTENDANCE (Phase 5.4):
#   join_booking:  sets joined_at (status stays confirmed)
#   leave_booking: sets left_at (requires joined_at)
#   finalize:      confirmed + joined_at -> attended
#                  confirmed + no joined_at -> no_show
#                  practice -> completed
#
# PURCHASE INTEGRATION (Phase 6.4):
#   create_booking: creates Purchase + double-entry ledger (always, even free)
#   finalize:       finalizes Purchases (unfreeze + commission)
#
# PROMO INTEGRATION (Phase 6.7 Batch 4):
#   create_booking: optional promo param, passed to create_purchase_for_booking.
#   Promo validation happens in the caller (router or purchase_router).
#
# CANCELLATION POLICY (Phase 6.5):
#   cancel_booking now handles refunds based on deadline:
#     > cancellation_deadline_hours before practice -> 100% refund
#     <= cancellation_deadline_hours before practice -> 0% refund (early finalize)
#   Both paths produce double-entry ledger entries (even for free practices).
#
# PARTICIPANT COUNT (Frontend Backlog A-03):
#   recalculate_participants() updates Practice.current_participants
#   after every booking status change.
#
# CAPACITY:
#   Checked via COUNT of active bookings, not current_participants (TD-034).
#
# WAITLIST INTEGRATION (Phase 5.3):
#   After cancelling a booking, process_waitlist is called.
#
# SESSION RULES:
#   No session.commit() here (P-01). Router handles flush + refresh.
#
# B-05: list_user_bookings uses subquery pattern for count (same as
#   list_user_checkins in diary/service.py). Eliminates parallel
#   count_base query that required manual filter duplication.
# =============================================================================

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING
from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import (
    BadRequestError,
    ConflictError,
    NotFoundError,
)
from app.modules.bookings.models import Booking, BookingStatus
from app.modules.payments.purchase import (
    create_purchase_for_booking,
    finalize_purchases,
)
from app.modules.payments.refund import (
    early_finalize_booking,
    refund_booking,
)
from app.modules.practices.models import Practice, PracticeStatus
from app.modules.promos.models import Promo
from app.modules.users.models import User

if TYPE_CHECKING:
    # Type-only import: the runtime import lives inside get_attendance to keep
    # the bookings -> diary dependency one-way (diary imports from bookings).
    from app.modules.diary.models import Checkin

logger = structlog.get_logger()

# Statuses that count toward capacity (for overbooking prevention).
_ACTIVE_BOOKING_STATUSES = {
    BookingStatus.PENDING.value,
    BookingStatus.CONFIRMED.value,
}

# Statuses from which cancellation is allowed.
_CANCELLABLE_STATUSES = {
    BookingStatus.PENDING.value,
    BookingStatus.CONFIRMED.value,
}

# Practice statuses that allow user check-in.
_JOINABLE_PRACTICE_STATUSES = {
    PracticeStatus.SCHEDULED.value,
    PracticeStatus.LIVE.value,
}

# Practice statuses that allow finalization.
_FINALIZABLE_PRACTICE_STATUSES = {
    PracticeStatus.SCHEDULED.value,
    PracticeStatus.LIVE.value,
}

# Statuses that count toward current_participants (display count).
# Different from _ACTIVE_BOOKING_STATUSES which includes pending
# for capacity checks. This counts who is actually "in" the practice.
# Consistent with Semaphore 3.4.
_PARTICIPANT_STATUSES = {
    BookingStatus.CONFIRMED.value,
    BookingStatus.ATTENDED.value,
}


async def _get_active_booking_count(
    session: AsyncSession,
    practice_id: UUID,
) -> int:
    """Count active bookings for a practice (TD-034)."""
    stmt = (
        select(func.count(Booking.id))
        .where(
            Booking.practice_id == practice_id,
            Booking.status.in_(_ACTIVE_BOOKING_STATUSES),
        )
    )
    result = await session.execute(stmt)
    return result.scalar_one()


async def recalculate_participants(
    practice_id: UUID,
    session: AsyncSession,
) -> int:
    """Recalculate and update Practice.current_participants.

    Counts bookings with status IN (confirmed, attended).
    Uses FOR UPDATE on Practice to prevent concurrent cached writes.

    This is the ONLY correct way to update current_participants.
    Analogous to balance recalculation in payments/service.py.

    Called after every booking status change:
      - create_booking (bookings/service.py)
      - cancel_booking (bookings/service.py)
      - finalize_practice (bookings/service.py)
      - confirm_waitlist (waitlist/service.py)
      - refund_all_bookings_for_practice (payments/refund.py)

    Returns the new participant count.
    """
    count_stmt = (
        select(func.count(Booking.id))
        .where(
            Booking.practice_id == practice_id,
            Booking.status.in_(_PARTICIPANT_STATUSES),
        )
    )
    result = await session.execute(count_stmt)
    count = result.scalar_one()

    # Lock practice row and update cached field.
    # Same pattern as balance recalculation (payments/service.py).
    practice = await session.get(
        Practice, practice_id, with_for_update=True,
    )
    if practice is not None:
        practice.current_participants = count
        await session.flush()

    logger.info(
        "participants_recalculated",
        practice_id=str(practice_id),
        current_participants=count,
    )

    return count


async def create_booking(
    user: User,
    practice_id: UUID,
    session: AsyncSession,
    promo: Promo | None = None,
) -> Booking:
    """Book a user into a practice.

    Validates:
    - Practice exists and is in scheduled/live status.
    - User is not the practice owner.
    - Practice is not full.
    - No active booking already exists (IntegrityError -> 409).

    Phase 6.7: optional promo for discount calculation.

    Uses begin_nested() (SAVEPOINT) to catch IntegrityError
    on the partial unique index without killing the outer transaction.
    """
    stmt = (
        select(Practice)
        .where(Practice.id == practice_id)
        .with_for_update()
    )
    result = await session.execute(stmt)
    practice = result.scalar_one_or_none()

    if not practice:
        raise NotFoundError("Practice not found")

    if practice.status not in _JOINABLE_PRACTICE_STATUSES:
        raise BadRequestError("Practice is not available for booking")

    # Time guard: a practice that has already started can no longer be booked.
    # The public feed (practices/service.py list_public_practices) hides
    # started/past practices, but the booking endpoints are reachable directly
    # by practice_id (e.g. opening a practice from "my bookings" history or a
    # deep link), so the feed filter is not enough. This is the single choke
    # point both POST /bookings and POST /practices/{id}/purchase go through,
    # so the guard here covers both paths. Threshold is the start
    # (scheduled_at), matching the feed. The status check above does not catch
    # this: a practice can still be `scheduled` past its start time when the
    # master never finalized it and the auto-finalizer has not run yet.
    if practice.scheduled_at <= datetime.now(timezone.utc):
        raise BadRequestError(
            "Cannot book a practice that has already started"
        )

    if practice.master_id == user.id:
        raise BadRequestError("Cannot book your own practice")

    active_count = await _get_active_booking_count(session, practice_id)
    # max_participants=None means unlimited capacity -- skip the check.
    if (
        practice.max_participants is not None
        and active_count >= practice.max_participants
    ):
        # F-03: unique code so frontend can switch on e.code instead of
        # string-matching the human-readable message.
        raise BadRequestError("Practice is full", code="practice_full")

    booking = Booking(
        practice_id=practice_id,
        user_id=user.id,
        status=BookingStatus.CONFIRMED.value,
    )
    session.add(booking)

    try:
        async with session.begin_nested():
            await session.flush()
    except IntegrityError:
        raise ConflictError(
            "Already booked for this practice"
        ) from None

    # Double-entry purchase (always, even for free practices).
    # Phase 6.7: pass promo for discount calculation.
    purchase = await create_purchase_for_booking(
        booking=booking,
        practice=practice,
        user=user,
        session=session,
        promo=promo,
    )

    # Update cached participant count (Frontend Backlog A-03).
    await recalculate_participants(practice_id, session)

    logger.info(
        "booking_created",
        booking_id=str(booking.id),
        purchase_id=str(purchase.id),
        practice_id=str(practice_id),
        user_id=str(user.id),
        status=booking.status,
        paid_cents=purchase.paid_cents,
        promo_code=promo.code if promo else None,
    )

    # Diary feed: project "user booked a practice" onto the user's timeline.
    # Lazy import keeps the dependency one-way (bookings -> diary) and avoids
    # an import cycle, same pattern as process_waitlist below.
    from app.modules.diary.projections import project_booking_confirmed
    from app.modules.masters.service import get_master_display_name
    master_name = await get_master_display_name(practice.master_id, session)
    await project_booking_confirmed(
        session,
        booking=booking,
        practice=practice,
        master_name=master_name,
        occurred_at=booking.created_at,
    )

    return booking


async def cancel_booking(
    booking_id: UUID,
    user: User,
    session: AsyncSession,
    reason: str | None = None,
) -> Booking:
    """Cancel a booking with refund policy enforcement.

    Only the booking owner can cancel. Only pending/confirmed
    bookings can be cancelled.

    Refund policy (Phase 6.5):
    - Cancel > cancellation_deadline_hours before practice:
      100% refund (Purchase -> REFUNDED).
    - Cancel <= cancellation_deadline_hours before practice:
      0% refund, early finalize (Purchase -> COMPLETED,
      master keeps money minus commission).

    Both paths create double-entry ledger entries, even for
    free practices (zero-amount entries as proof of path).

    After cancellation, triggers waitlist processing to notify
    the next waiting user (Phase 5.3).

    Uses FOR UPDATE to prevent concurrent cancellation (P-12).
    """
    stmt = (
        select(Booking)
        .where(Booking.id == booking_id)
        .with_for_update()
    )
    result = await session.execute(stmt)
    booking = result.scalar_one_or_none()

    if not booking:
        raise NotFoundError("Booking not found")

    # P-08: 404 not 403 to avoid revealing booking existence.
    if booking.user_id != user.id:
        raise NotFoundError("Booking not found")

    if booking.status not in _CANCELLABLE_STATUSES:
        raise BadRequestError(
            f"Cannot cancel booking in status "
            f"{booking.status}"
        )

    booking.status = BookingStatus.CANCELLED.value
    booking.cancelled_at = datetime.now(timezone.utc)
    booking.cancellation_reason = reason

    # Phase 6.5: Refund or early-finalize based on deadline.
    # Load practice for scheduled_at (read-only, no FOR UPDATE needed).
    practice_stmt = (
        select(Practice)
        .where(Practice.id == booking.practice_id)
    )
    practice = (
        await session.execute(practice_stmt)
    ).scalar_one()

    # Fix 2.3: scheduled_at is NOT NULL in the model, but guard against
    # incomplete ORM objects (e.g. partial loads in tests). Treat missing
    # scheduled_at as early cancel (full refund) -- the safe default.
    if practice.scheduled_at is None:
        logger.warning(
            "cancel_booking_missing_scheduled_at",
            booking_id=str(booking_id),
            practice_id=str(booking.practice_id),
        )
        await refund_booking(
            booking=booking,
            practice=practice,
            session=session,
        )
    else:
        deadline = practice.scheduled_at - timedelta(
            hours=settings.cancellation_deadline_hours,
        )
        now = datetime.now(timezone.utc)

        if now < deadline:
            # Early cancel: full refund.
            await refund_booking(
                booking=booking,
                practice=practice,
                session=session,
            )
            logger.info(
                "booking_cancelled_with_refund",
                booking_id=str(booking_id),
                user_id=str(user.id),
                reason=reason,
            )
        else:
            # Late cancel: master keeps the money (early finalize).
            await early_finalize_booking(
                booking=booking,
                practice=practice,
                session=session,
            )
            logger.info(
                "booking_cancelled_no_refund",
                booking_id=str(booking_id),
                user_id=str(user.id),
                reason=reason,
            )

    # Update cached participant count (Frontend Backlog A-03).
    await recalculate_participants(booking.practice_id, session)

    # Phase 5.3: Notify next waiting user in the queue.
    from app.modules.waitlist.service import process_waitlist
    await process_waitlist(booking.practice_id, session)

    # Diary feed: project "user cancelled their booking" onto the timeline.
    # occurred_at is the cancellation instant (set above). Lazy import keeps
    # the dependency one-way (bookings -> diary).
    from app.modules.diary.projections import project_booking_cancelled
    from app.modules.masters.service import get_master_display_name
    master_name = await get_master_display_name(practice.master_id, session)
    await project_booking_cancelled(
        session,
        booking=booking,
        practice=practice,
        master_name=master_name,
        occurred_at=booking.cancelled_at,
    )

    return booking


# ===================================================================
# Phase 5.4: Attendance
# ===================================================================


async def join_booking(
    booking_id: UUID,
    user: User,
    session: AsyncSession,
) -> Booking:
    """Mark user as joined (check-in).

    Sets joined_at timestamp. Status stays confirmed -- the
    transition to attended happens at finalize.

    Validates:
    - Booking exists and belongs to user (P-08).
    - Status is confirmed.
    - Practice is in joinable state (scheduled/live).
    - Not already joined (409).

    Uses FOR UPDATE (P-12).
    """
    stmt = (
        select(Booking)
        .where(Booking.id == booking_id)
        .with_for_update()
    )
    result = await session.execute(stmt)
    booking = result.scalar_one_or_none()

    if not booking:
        raise NotFoundError("Booking not found")

    if booking.user_id != user.id:
        raise NotFoundError("Booking not found")

    if booking.status != BookingStatus.CONFIRMED.value:
        raise BadRequestError(
            "Can only join a confirmed booking"
        )

    if booking.joined_at is not None:
        raise ConflictError("Already joined")

    # Check practice is in joinable state.
    practice_stmt = (
        select(Practice)
        .where(Practice.id == booking.practice_id)
    )
    practice = (
        await session.execute(practice_stmt)
    ).scalar_one()

    if practice.status not in _JOINABLE_PRACTICE_STATUSES:
        raise BadRequestError("Cannot join this practice")

    booking.joined_at = datetime.now(timezone.utc)

    logger.info(
        "booking_joined",
        booking_id=str(booking_id),
        user_id=str(user.id),
        practice_id=str(booking.practice_id),
    )

    return booking


async def leave_booking(
    booking_id: UUID,
    user: User,
    session: AsyncSession,
) -> Booking:
    """Mark user as left.

    Sets left_at timestamp. Requires joined_at to be set.

    Validates:
    - Booking exists and belongs to user (P-08).
    - joined_at is set (400 if not).
    - left_at is not already set (409).

    Uses FOR UPDATE (P-12).
    """
    stmt = (
        select(Booking)
        .where(Booking.id == booking_id)
        .with_for_update()
    )
    result = await session.execute(stmt)
    booking = result.scalar_one_or_none()

    if not booking:
        raise NotFoundError("Booking not found")

    if booking.user_id != user.id:
        raise NotFoundError("Booking not found")

    if booking.joined_at is None:
        raise BadRequestError(
            "Cannot leave without joining first"
        )

    if booking.left_at is not None:
        raise ConflictError("Already left")

    booking.left_at = datetime.now(timezone.utc)

    logger.info(
        "booking_left",
        booking_id=str(booking_id),
        user_id=str(user.id),
        practice_id=str(booking.practice_id),
    )

    return booking


async def _finalize_practice_core(
    practice: Practice,
    session: AsyncSession,
    *,
    actor: str,
) -> Practice:
    """Shared finalization logic -- NO authorization, NO practice loading.

    Caller MUST pass a practice that is already loaded FOR UPDATE and already
    validated to be in a finalizable state (_FINALIZABLE_PRACTICE_STATUSES).
    This is the single source of truth for what "finalizing a practice" means,
    shared by the manual master path (finalize_practice) and the system
    auto-close path (auto_finalize_practice). Keeping one core guarantees the
    two paths can never drift in how attendance, money, or the diary are
    settled.

    Transitions:
    - confirmed + joined_at IS NOT NULL -> attended
    - confirmed + joined_at IS NULL     -> no_show
    - Practice status -> completed
    - All pending purchases -> completed (unfreeze + commission)

    `actor` is logged only (e.g. "master" / "system") -- it does not change
    behavior. Session rules unchanged (P-01): no commit here.
    """
    practice_id = practice.id

    # Bulk update: confirmed + joined -> attended, else -> no_show.
    bookings_stmt = (
        select(Booking)
        .where(
            Booking.practice_id == practice_id,
            Booking.status == BookingStatus.CONFIRMED.value,
        )
        .with_for_update()
    )
    bookings_result = await session.execute(bookings_stmt)
    bookings = bookings_result.scalars().all()

    attended_count = 0
    no_show_count = 0
    # Collect (user_id, booking_id, status) for the diary feed projection.
    # We capture the resolved outcome per booking so each booker gets a card
    # showing Done (attended) or "Не состоялась" (no_show).
    outcomes: list[tuple[UUID, UUID, str]] = []

    for booking in bookings:
        if booking.joined_at is not None:
            booking.status = BookingStatus.ATTENDED.value
            attended_count += 1
        else:
            booking.status = BookingStatus.NO_SHOW.value
            no_show_count += 1
        outcomes.append(
            (booking.user_id, booking.id, booking.status)
        )

    practice.status = PracticeStatus.COMPLETED.value

    # Finalize all purchases: unfreeze + commission (double-entry).
    finalized = await finalize_purchases(
        practice_id=practice_id,
        practice=practice,
        session=session,
    )

    # Update cached participant count (Frontend Backlog A-03).
    # After finalize: attended stays in count, no_show drops out.
    await recalculate_participants(practice_id, session)

    logger.info(
        "practice_finalized",
        practice_id=str(practice_id),
        actor=actor,
        attended=attended_count,
        no_show=no_show_count,
        purchases_finalized=len(finalized),
    )

    # Diary feed: project the finalization outcome onto each booker's
    # timeline (attended -> Done, no_show -> "Не состоялась"). occurred_at is
    # the finalization instant. Lazy import keeps the dependency one-way.
    from app.modules.diary.projections import project_practice_outcome
    from app.modules.masters.service import get_master_display_name
    master_name = await get_master_display_name(practice.master_id, session)
    await project_practice_outcome(
        session,
        practice=practice,
        master_name=master_name,
        outcomes=outcomes,
        occurred_at=datetime.now(timezone.utc),
    )

    return practice


async def finalize_practice(
    practice_id: UUID,
    user: User,
    session: AsyncSession,
) -> Practice:
    """Finalize a practice -- set attendance statuses + financial settlement.

    Master-only manual path. Loads + locks the practice, enforces ownership
    (P-08) and finalizable state, then delegates the actual settlement to
    _finalize_practice_core. The auto-close worker uses the same core via
    auto_finalize_practice (no ownership check).

    Validates:
    - Practice exists and belongs to master (P-08: 404).
    - Practice is in finalizable state (scheduled/live).

    Uses FOR UPDATE on practice (P-12).
    """
    stmt = (
        select(Practice)
        .where(Practice.id == practice_id)
        .with_for_update()
    )
    result = await session.execute(stmt)
    practice = result.scalar_one_or_none()

    if not practice:
        raise NotFoundError("Practice not found")

    # P-08: 404 not 403 for non-owner.
    if practice.master_id != user.id:
        raise NotFoundError("Practice not found")

    if practice.status not in _FINALIZABLE_PRACTICE_STATUSES:
        raise BadRequestError("Practice already finalized")

    return await _finalize_practice_core(practice, session, actor="master")


async def auto_finalize_practice(
    practice_id: UUID,
    session: AsyncSession,
) -> Practice:
    """System path: finalize a practice without a master actor.

    Used by the auto-finalization worker for practices that ran past the
    24h ceiling and were never closed by their master. There is no User and
    no ownership check (the actor is the system, mirroring how the Stripe
    webhook acts: actor_type="system", actor_id=None). Authorization is
    intentionally absent -- this function must never be exposed via an
    HTTP route.

    Loads + locks the practice and verifies it is still finalizable (another
    worker tick or a concurrent manual finalize may have closed it first, in
    which case we raise BadRequestError and the caller skips it). Delegates
    settlement to the shared _finalize_practice_core. Session rules unchanged
    (P-01): no commit here -- the worker's session owns the transaction.
    """
    stmt = (
        select(Practice)
        .where(Practice.id == practice_id)
        .with_for_update()
    )
    result = await session.execute(stmt)
    practice = result.scalar_one_or_none()

    if not practice:
        raise NotFoundError("Practice not found")

    if practice.status not in _FINALIZABLE_PRACTICE_STATUSES:
        raise BadRequestError("Practice already finalized")

    return await _finalize_practice_core(practice, session, actor="system")


async def get_attendance(
    practice_id: UUID,
    user: User,
    session: AsyncSession,
) -> tuple[Practice, list[Booking], dict[UUID, User], dict[UUID, "Checkin"]]:
    """Get attendance list for a practice (master-only), enriched for prep.

    Returns all non-cancelled bookings with attendance data, plus two lookup
    maps the master's prep view needs per participant:
      - users:    user_id -> User, so the router can show a name + avatar
                  instead of a bare user_id.
      - checkins: booking_id -> PRE Checkin, the participant's pre-practice
                  check-in (mood + comment), when they left one.

    Both maps are built with one batch query each (id IN (...)), so the
    endpoint stays N+1-free no matter how many participants there are.

    PRIVACY: exposing each participant's PRE check-in to the master is
    intentional and scoped to this practice only. Ownership is enforced
    immediately below (P-08), and the check-in batch is keyed on this
    practice's booking_ids, so no cross-practice data can leak. Global
    check-in privacy (GET /users/me/checkins -- own-only) is untouched.

    Validates:
    - Practice exists and belongs to master (P-08: 404).
    """
    # Local import keeps the bookings -> diary dependency one-way (diary
    # already imports from bookings), same pattern as list_user_bookings.
    from app.modules.diary.models import Checkin
    from app.modules.diary.service import get_pre_checkins_for_bookings

    practice = await session.get(Practice, practice_id)

    if not practice:
        raise NotFoundError("Practice not found")

    if practice.master_id != user.id:
        raise NotFoundError("Practice not found")

    stmt = (
        select(Booking)
        .where(
            Booking.practice_id == practice_id,
            Booking.status != BookingStatus.CANCELLED.value,
        )
        .order_by(Booking.created_at)
    )
    result = await session.execute(stmt)
    bookings = list(result.scalars().all())

    # Batch-load participants (one query) so the router can render names.
    user_ids = [b.user_id for b in bookings]
    users: dict[UUID, User] = {}
    if user_ids:
        users_result = await session.execute(
            select(User).where(User.id.in_(user_ids))
        )
        users = {u.id: u for u in users_result.scalars().all()}

    # Batch-load PRE check-ins (one query) keyed by booking_id.
    booking_ids = [b.id for b in bookings]
    checkins: dict[UUID, Checkin] = await get_pre_checkins_for_bookings(
        booking_ids, session,
    )

    return practice, bookings, users, checkins


# ===================================================================
# Frontend Backlog: list / detail
# ===================================================================


async def list_user_bookings(
    user: User,
    session: AsyncSession,
    *,
    status_filter: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[tuple[Booking, Practice, bool, bool]], int]:
    """List bookings for a user with practice details (paginated).

    B-05: count derived from base query subquery instead of maintaining
    a parallel count_base with duplicated filter clauses. Same pattern
    as list_user_checkins in diary/service.py.

    Each row also carries two diary-state flags for the dashboard banners:
      - has_feedback: the user already left a feedback for this practice.
      - has_checkin:  the user already did a PRE check-in for this booking.
    They let the dashboard hide the "оставьте feedback" / "пора на check-in"
    prompt once done (and stop re-submitting through a stale banner). Computed
    with two set-membership queries over the current page -- no N+1.

    Returns:
        Tuple of (list of (Booking, Practice, has_feedback, has_checkin)
        tuples, total count).
    """
    # Local import keeps the bookings -> diary dependency one-way and avoids
    # any import-order surprise (diary.projections imports bookings lazily).
    from app.modules.diary.models import Checkin, CheckType, Feedback

    base = (
        select(Booking, Practice)
        .join(Practice, Booking.practice_id == Practice.id)
        .where(Booking.user_id == user.id)
    )

    if status_filter:
        base = base.where(Booking.status == status_filter)

    # Count via subquery -- filters applied exactly once, no duplication.
    total = (
        await session.execute(
            select(func.count()).select_from(base.subquery())
        )
    ).scalar_one()

    items_stmt = (
        base
        .order_by(Booking.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(items_stmt)
    page = [(row[0], row[1]) for row in result.all()]

    # Diary-state flags for this page (set membership -- no per-row query).
    practice_ids = [b.practice_id for b, _ in page]
    booking_ids = [b.id for b, _ in page]

    feedback_practice_ids: set[UUID] = set()
    if practice_ids:
        feedback_practice_ids = set(
            (
                await session.execute(
                    select(Feedback.practice_id)
                    .where(
                        Feedback.user_id == user.id,
                        Feedback.practice_id.in_(practice_ids),
                    )
                    .distinct()
                )
            ).scalars().all()
        )

    checkin_booking_ids: set[UUID] = set()
    if booking_ids:
        checkin_booking_ids = set(
            (
                await session.execute(
                    select(Checkin.booking_id)
                    .where(
                        Checkin.booking_id.in_(booking_ids),
                        Checkin.check_type == CheckType.PRE.value,
                    )
                    .distinct()
                )
            ).scalars().all()
        )

    items = [
        (
            booking,
            practice,
            booking.practice_id in feedback_practice_ids,
            booking.id in checkin_booking_ids,
        )
        for booking, practice in page
    ]

    return items, total


async def get_booking_by_id(
    booking_id: UUID,
    user: User,
    session: AsyncSession,
) -> tuple[Booking, Practice]:
    """Get a single booking with full practice details.

    Access control:
    - Booking owner.
    - Master of the associated practice.

    Returns 404 for non-existent or unauthorized bookings (P-08).
    """
    stmt = (
        select(Booking, Practice)
        .join(Practice, Booking.practice_id == Practice.id)
        .where(Booking.id == booking_id)
    )
    result = await session.execute(stmt)
    row = result.one_or_none()

    if not row:
        raise NotFoundError("Booking not found")

    booking, practice = row[0], row[1]

    # P-08: owner or practice master.
    if booking.user_id != user.id and practice.master_id != user.id:
        raise NotFoundError("Booking not found")

    return booking, practice


# ===================================================================
# Profile stats (Screen A: main profile)
# ===================================================================


async def get_user_practice_stats(
    user: User,
    session: AsyncSession,
) -> tuple[int, float]:
    """Aggregate the user's attended-practice stats for the profile screen.

    Returns (practices_attended, hours_attended):
      - practices_attended: count of the user's bookings with status=attended.
      - hours_attended: sum of those practices' duration_minutes / 60,
        rounded to one decimal (mockup shows e.g. "9.5").

    Single ORM query (count + coalesced sum) joined practices<->bookings.
    Only attended bookings count, so the two numbers stay consistent
    (a practice contributes to both the count and the hours, or neither).
    coalesce keeps sum at 0 (not NULL) when the user has no attended
    bookings, so the empty case returns (0, 0.0).
    """
    stmt = (
        select(
            func.count(Booking.id),
            func.coalesce(func.sum(Practice.duration_minutes), 0),
        )
        .join(Practice, Booking.practice_id == Practice.id)
        .where(
            Booking.user_id == user.id,
            Booking.status == BookingStatus.ATTENDED.value,
        )
    )
    result = await session.execute(stmt)
    practices_attended, total_minutes = result.one()

    hours_attended = round(int(total_minutes) / 60, 1)
    return int(practices_attended), hours_attended
