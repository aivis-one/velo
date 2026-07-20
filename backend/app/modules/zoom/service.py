# =============================================================================
# VELO Backend -- Zoom Meeting + Registrant Lifecycle (E21 steps D + E)
# =============================================================================
#
# Best-effort glue between the practice/booking lifecycle
# (practices/service.py, practices/cancel_service.py, bookings/service.py)
# and the Zoom API (zoom_client.py). Every function here NEVER RAISES -- a
# Zoom failure is caught, logged, and recorded on the relevant row so it
# stays visible and retryable (create failures) or is simply logged
# (reschedule/delete/cancel failures, which don't block anything downstream
# in this step). This is the whole point: publish/reschedule/cancel/book
# must never be blocked by a third party (E21 plan sec 2/3, confirmed as
# the intended reading in ПРОМТ №519, restated explicitly for booking in
# ПРОМТ №520: "do not soften it into 'usually'").
#
# HOST EXCLUSION (step E): ensure_host_registrant registers the practice's
# master through the SAME Zoom flow as a student, role='host', no
# booking_id. This is the ENTIRE mechanism -- Zoom exposes no host flag on
# any surface (E21 research, round 2), so ours is the only fact that
# exists. Called after every successful meeting creation, idempotent (a
# no-op if a host row already exists), so it fires exactly once per meeting
# regardless of whether that meeting was created on the first attempt or a
# later retry.
#
# NO EMAIL ON VELO USERS (real gap, not hidden): User has no dedicated
# email column -- E11 added an OPTIONAL email in the credentials JSONB via
# a profile-edit form, so most users likely have none. Zoom's registrant
# API requires email. _registration_email_for falls back to a
# structurally-valid, deliberately-unusable placeholder
# (RFC 2606 .invalid TLD) when the user has no real one. KNOWN CONSEQUENCE:
# the future matching ladder's email-fallback step will not work for any
# VELO user who joins Zoom without going through our personal link (i.e.
# by authenticating with their own real Zoom account under their real
# email) -- that email will never match our placeholder. This narrows the
# ladder's real fallback value toward registrant_id only, which the owner
# should know before sizing the unmatched bucket, not discover after.
#
# SESSION RULES: no session.commit() here (P-01, same convention as every
# other service module) -- callers manage the transaction. Every function
# below add/mutates ORM objects on the session passed in; the caller's
# existing commit picks them up.
# =============================================================================

from datetime import UTC

import structlog
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.bookings.models import Booking
from app.modules.practices.models import Practice
from app.modules.users.models import User
from app.modules.zoom.models import (
    ZoomAttendanceSegment,
    ZoomMeeting,
    ZoomMeetingStatus,
    ZoomRegistrant,
    ZoomRegistrantRole,
    ZoomRegistrantStatus,
)
from app.modules.zoom.zoom_client import (
    ZoomAPIError,
    create_meeting,
    create_registrant,
    delete_meeting,
    list_registrants,
    patch_meeting,
    update_registrant_status,
)

logger = structlog.get_logger()


def _registration_email_for(user: User) -> str:
    """The exact email we will send Zoom for this user -- see module
    docstring for why a placeholder is sometimes unavoidable. Frozen into
    ZoomRegistrant.registration_email at the call site, not re-derived
    later."""
    real_email = (user.credentials or {}).get("email")
    if real_email:
        return real_email
    return f"user-{user.id}@users.velo.invalid"


async def create_meeting_for_practice(
    practice: Practice,
    session: AsyncSession,
) -> ZoomMeeting:
    """Create the Zoom meeting for a practice being published.

    Always returns a ZoomMeeting row (added to `session`, not committed) --
    status=active on success, status=create_failed + last_sync_error on any
    failure. Never raises: the caller (update_practice's publish branch)
    must succeed regardless of Zoom's outcome.
    """
    row = ZoomMeeting(practice_id=practice.id)
    session.add(row)

    try:
        response = await create_meeting(
            topic=practice.title,
            start_time_iso=practice.scheduled_at.astimezone(UTC).isoformat(),
            duration_minutes=practice.duration_minutes,
            timezone=practice.timezone,
        )
        row.zoom_meeting_id = str(response.get("id"))
        row.zoom_meeting_uuid = response.get("uuid")
        row.host_zoom_user_id = response.get("host_id")
        row.status = ZoomMeetingStatus.ACTIVE.value
        logger.info(
            "zoom_meeting_created",
            practice_id=str(practice.id),
            zoom_meeting_id=row.zoom_meeting_id,
        )
        await ensure_host_registrant(row, practice, session)
    except ZoomAPIError as exc:
        row.status = ZoomMeetingStatus.CREATE_FAILED.value
        row.last_sync_error = (
            f"create_meeting failed: status={exc.status_code} body={exc.body}"
        )
        logger.warning(
            "zoom_meeting_create_failed",
            practice_id=str(practice.id),
            status_code=exc.status_code,
        )
    except Exception:
        # ПРОМТ №525: ensure_host_registrant is now self-contained (its own
        # savepoint absorbs a database-level conflict, see that function),
        # but the module docstring's "NEVER RAISES" is a blanket contract --
        # anything else unforeseen here must not escape either, or publish
        # (or series generation, which calls this per child) can still be
        # aborted by our own code the same way the incident showed it could.
        row.status = ZoomMeetingStatus.CREATE_FAILED.value
        row.last_sync_error = "create_meeting_for_practice: unexpected error"
        logger.exception(
            "zoom_meeting_create_unexpected_error",
            practice_id=str(practice.id),
        )

    return row


async def ensure_host_registrant(
    zoom_meeting: ZoomMeeting,
    practice: Practice,
    session: AsyncSession,
) -> None:
    """Create the practice's master as a role='host' registrant, exactly
    once per meeting.

    Idempotent by design (checks for an existing, non-cancelled host row
    first) so it is safe to call from BOTH the initial successful creation
    (create_meeting_for_practice above) AND a later successful retry
    (retry_poller._attempt_create) without ever double-registering the
    master. See module docstring -- this is the entire host-exclusion
    mechanism.

    ПРОМТ №525: the existence check above is TOCTOU-safe only up to the
    point of the actual insert -- a concurrent caller (or, as the incident
    that prompted this, a caller that seeded a conflicting row directly)
    can still lose a genuine race to
    uq_zoom_registrant_meeting_user_active. The insert itself runs inside
    session.begin_nested() (a SAVEPOINT) specifically so that a
    unique-violation there can be rolled back to the savepoint and
    swallowed, instead of leaving the CALLER's own transaction unusable
    (PendingRollbackError) -- a plain try/except around the flush is not
    enough by itself: catching the Python exception does not undo the
    database-level abort without something to roll back TO. Best-effort:
    never raises, for exactly this reason ("Zoom never blocks" has to hold
    for our own database, not only Zoom's API).
    """
    existing = (
        await session.execute(
            select(ZoomRegistrant.id).where(
                ZoomRegistrant.zoom_meeting_id == zoom_meeting.id,
                ZoomRegistrant.role == ZoomRegistrantRole.HOST.value,
                ZoomRegistrant.status != ZoomRegistrantStatus.CANCELLED.value,
            ).limit(1)
        )
    ).first()
    if existing is not None:
        return

    master_user = await session.get(User, practice.master_id)
    if master_user is None:
        logger.warning(
            "zoom_host_registrant_skipped_no_master",
            practice_id=str(practice.id),
        )
        return

    email = _registration_email_for(master_user)

    try:
        async with session.begin_nested():
            row = ZoomRegistrant(
                zoom_meeting_id=zoom_meeting.id,
                user_id=master_user.id,
                booking_id=None,
                role=ZoomRegistrantRole.HOST.value,
                registration_email=email,
                status=ZoomRegistrantStatus.PENDING.value,
            )
            session.add(row)
            await session.flush()
    except IntegrityError:
        # Lost the race for this (meeting, user) slot -- someone else (a
        # concurrent call, or a pre-existing non-host row for the same
        # user) already holds it. Nothing left for THIS call to do; the
        # savepoint rollback is what keeps the caller's own transaction
        # alive past this point.
        logger.info(
            "zoom_host_registrant_race_lost", practice_id=str(practice.id),
        )
        return

    try:
        response = await create_registrant(
            zoom_meeting_id=zoom_meeting.zoom_meeting_id,
            email=email,
            first_name=master_user.first_name or "VELO",
            last_name=master_user.last_name or "Master",
        )
        row.zoom_registrant_id = response.get("registrant_id") or response.get("id")
        row.join_url = response.get("join_url")
        row.status = ZoomRegistrantStatus.REGISTERED.value
        logger.info(
            "zoom_host_registrant_created",
            practice_id=str(practice.id),
            zoom_registrant_id=row.zoom_registrant_id,
        )
    except ZoomAPIError as exc:
        row.status = ZoomRegistrantStatus.CREATE_FAILED.value
        row.last_sync_error = (
            f"host registrant create failed: "
            f"status={exc.status_code} body={exc.body}"
        )
        logger.warning(
            "zoom_host_registrant_create_failed",
            practice_id=str(practice.id),
            status_code=exc.status_code,
        )
    except Exception:
        row.status = ZoomRegistrantStatus.CREATE_FAILED.value
        row.last_sync_error = "host registrant create failed: unexpected error"
        logger.exception(
            "zoom_host_registrant_unexpected_error",
            practice_id=str(practice.id),
        )


async def create_registrant_for_booking(
    booking: Booking,
    user: User,
    session: AsyncSession,
) -> ZoomRegistrant | None:
    """Create the Zoom registrant for a student's booking.

    Idempotent by (zoom_meeting_id, user_id) -- looks up an existing,
    non-cancelled registrant for this pair FIRST and reuses it instead of
    inserting a second row (ПРОМТ №525: this check was missing entirely
    before, the same non-idempotent shape that broke ensure_host_registrant,
    just never triggered here yet -- the bookings table's own
    uq_booking_practice_user_active makes two ACTIVE bookings for the same
    (practice, user) impossible today, so the realistic trigger is a
    retried call for the SAME booking, not a second booking). Insert only
    when none exists (added to `session`, not committed) -- status=registered
    on success, status=pending if the meeting isn't ACTIVE yet (queued for
    the retry poller's registrant phase), status=create_failed if Zoom's
    call itself failed (also retried by the poller). Returns None when
    there is no ZoomMeeting row at all for this practice (pre-E21 data, or
    a series-child edge case), or when the insert lost a race for the slot.

    NEVER RAISES and never blocks booking creation, regardless of Zoom's
    or the meeting's state (ПРОМТ №519 amendment 2 / ПРОМТ №520: not
    softened into "usually"). The insert itself runs inside
    session.begin_nested() (a SAVEPOINT) for the same reason as
    ensure_host_registrant: catching the exception alone would not be
    enough to keep the CALLER's transaction (the booking that already
    succeeded) alive past a unique-violation here.
    """
    zoom_meeting = (
        await session.execute(
            select(ZoomMeeting).where(ZoomMeeting.practice_id == booking.practice_id)
        )
    ).scalar_one_or_none()
    if zoom_meeting is None:
        logger.info(
            "zoom_registrant_skipped_no_meeting", booking_id=str(booking.id),
        )
        return None

    existing = (
        await session.execute(
            select(ZoomRegistrant).where(
                ZoomRegistrant.zoom_meeting_id == zoom_meeting.id,
                ZoomRegistrant.user_id == user.id,
                ZoomRegistrant.status != ZoomRegistrantStatus.CANCELLED.value,
            )
        )
    ).scalar_one_or_none()
    if existing is not None:
        logger.info(
            "zoom_registrant_reused_existing", booking_id=str(booking.id),
        )
        return existing

    email = _registration_email_for(user)

    try:
        async with session.begin_nested():
            row = ZoomRegistrant(
                zoom_meeting_id=zoom_meeting.id,
                user_id=user.id,
                booking_id=booking.id,
                role=ZoomRegistrantRole.STUDENT.value,
                registration_email=email,
                status=ZoomRegistrantStatus.PENDING.value,
            )
            session.add(row)
            await session.flush()
    except IntegrityError:
        logger.info("zoom_registrant_race_lost", booking_id=str(booking.id))
        return None

    if zoom_meeting.status != ZoomMeetingStatus.ACTIVE.value:
        # Meeting not ready yet -- leave queued (status stays PENDING) for
        # the retry poller. Booking already succeeded; this is a queue
        # entry, not a failure.
        logger.info(
            "zoom_registrant_queued_meeting_not_active",
            booking_id=str(booking.id),
        )
        return row

    try:
        response = await create_registrant(
            zoom_meeting_id=zoom_meeting.zoom_meeting_id,
            email=email,
            first_name=user.first_name or "VELO",
            last_name=user.last_name or "User",
        )
        row.zoom_registrant_id = response.get("registrant_id") or response.get("id")
        row.join_url = response.get("join_url")
        row.status = ZoomRegistrantStatus.REGISTERED.value
        logger.info(
            "zoom_registrant_created",
            booking_id=str(booking.id),
            zoom_registrant_id=row.zoom_registrant_id,
        )
    except ZoomAPIError as exc:
        row.status = ZoomRegistrantStatus.CREATE_FAILED.value
        row.last_sync_error = (
            f"create_registrant failed: status={exc.status_code} body={exc.body}"
        )
        logger.warning(
            "zoom_registrant_create_failed",
            booking_id=str(booking.id),
            status_code=exc.status_code,
        )
    except Exception:
        row.status = ZoomRegistrantStatus.CREATE_FAILED.value
        row.last_sync_error = "create_registrant failed: unexpected error"
        logger.exception(
            "zoom_registrant_unexpected_error", booking_id=str(booking.id),
        )

    return row


async def cancel_registrant_for_booking(
    booking: Booking,
    session: AsyncSession,
) -> None:
    """Best-effort Zoom-side registrant cancel; mark our own row cancelled
    REGARDLESS of whether the Zoom call succeeds.

    Our row's status is the sole authority downstream (E21 research: it was
    never confirmed whether Zoom actually invalidates a cancelled
    registrant's join link -- nothing here may depend on Zoom cooperating).
    No-op if there's no registrant row for this booking. Never raises --
    booking cancellation must proceed regardless.
    """
    row = (
        await session.execute(
            select(ZoomRegistrant).where(ZoomRegistrant.booking_id == booking.id)
        )
    ).scalar_one_or_none()
    if row is None:
        return

    if row.zoom_registrant_id:
        zoom_meeting = await session.get(ZoomMeeting, row.zoom_meeting_id)
        if zoom_meeting is not None and zoom_meeting.zoom_meeting_id:
            try:
                await update_registrant_status(
                    zoom_meeting_id=zoom_meeting.zoom_meeting_id,
                    zoom_registrant_id=row.zoom_registrant_id,
                    email=row.registration_email,
                    action="cancel",
                )
            except ZoomAPIError as exc:
                logger.warning(
                    "zoom_registrant_cancel_call_failed",
                    booking_id=str(booking.id),
                    status_code=exc.status_code,
                )

    row.status = ZoomRegistrantStatus.CANCELLED.value
    logger.info("zoom_registrant_cancelled", booking_id=str(booking.id))


async def sync_meeting_reschedule(
    practice: Practice,
    session: AsyncSession,
) -> None:
    """PATCH the Zoom meeting's start time, then re-fetch registrants and
    overwrite our stored join_url with whatever Zoom currently returns.

    This is the self-healing answer to the unresolved question of whether
    registrant links survive a reschedule (E21 research could not confirm
    either way): if links survived, re-fetching is a no-op; if they didn't,
    we pick up the fresh ones without needing to have known which world we
    were in. No-op (logged, not raised) if there's no active ZoomMeeting for
    this practice yet, or if either Zoom call fails.
    """
    zoom_meeting = (
        await session.execute(
            select(ZoomMeeting).where(ZoomMeeting.practice_id == practice.id)
        )
    ).scalar_one_or_none()

    if zoom_meeting is None or zoom_meeting.status != ZoomMeetingStatus.ACTIVE.value:
        # No active meeting to reschedule -- either creation never
        # succeeded (retry poller owns that) or this practice predates E21.
        return

    try:
        await patch_meeting(
            zoom_meeting_id=zoom_meeting.zoom_meeting_id,
            start_time_iso=practice.scheduled_at.astimezone(UTC).isoformat(),
        )
    except ZoomAPIError as exc:
        zoom_meeting.last_sync_error = (
            f"patch_meeting (reschedule) failed: "
            f"status={exc.status_code} body={exc.body}"
        )
        logger.warning(
            "zoom_meeting_reschedule_failed",
            practice_id=str(practice.id),
            status_code=exc.status_code,
        )
        return

    try:
        registrants = await list_registrants(zoom_meeting_id=zoom_meeting.zoom_meeting_id)
    except ZoomAPIError as exc:
        logger.warning(
            "zoom_registrant_refetch_failed",
            practice_id=str(practice.id),
            status_code=exc.status_code,
        )
        return

    if not registrants:
        return

    stored = (
        await session.execute(
            select(ZoomRegistrant).where(
                ZoomRegistrant.zoom_meeting_id == zoom_meeting.id,
            )
        )
    ).scalars().all()
    by_zoom_id = {r.zoom_registrant_id: r for r in stored if r.zoom_registrant_id}

    for remote in registrants:
        remote_id = remote.get("registrant_id") or remote.get("id")
        local = by_zoom_id.get(remote_id)
        if local is None:
            continue
        fresh_join_url = remote.get("join_url")
        if fresh_join_url and fresh_join_url != local.join_url:
            local.join_url = fresh_join_url

    logger.info(
        "zoom_registrants_refetched",
        practice_id=str(practice.id),
        remote_count=len(registrants),
    )


async def delete_meeting_for_practice(
    practice: Practice,
    session: AsyncSession,
) -> None:
    """Best-effort deletion of a practice's Zoom meeting on cancel.

    Skips meetings that already have attendance segments (nothing left to
    protect a cancelled-after-the-fact meeting from -- the report already
    happened). No-op if there's no active meeting, or if the Zoom call
    fails (logged, never raised -- refunds/cancellation must proceed
    regardless, E21 plan sec 2).
    """
    zoom_meeting = (
        await session.execute(
            select(ZoomMeeting).where(ZoomMeeting.practice_id == practice.id)
        )
    ).scalar_one_or_none()

    if zoom_meeting is None or zoom_meeting.status != ZoomMeetingStatus.ACTIVE.value:
        return

    has_segments = (
        await session.execute(
            select(ZoomAttendanceSegment.id)
            .where(ZoomAttendanceSegment.zoom_meeting_id == zoom_meeting.id)
            .limit(1)
        )
    ).first() is not None
    if has_segments:
        logger.info(
            "zoom_meeting_delete_skipped_has_segments",
            practice_id=str(practice.id),
        )
        return

    try:
        await delete_meeting(zoom_meeting_id=zoom_meeting.zoom_meeting_id)
        zoom_meeting.status = ZoomMeetingStatus.DELETED.value
        logger.info("zoom_meeting_deleted", practice_id=str(practice.id))
    except ZoomAPIError as exc:
        zoom_meeting.last_sync_error = (
            f"delete_meeting failed: status={exc.status_code} body={exc.body}"
        )
        logger.warning(
            "zoom_meeting_delete_failed",
            practice_id=str(practice.id),
            status_code=exc.status_code,
        )
