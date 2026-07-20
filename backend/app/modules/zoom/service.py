# =============================================================================
# VELO Backend -- Zoom Meeting Lifecycle (E21 step D)
# =============================================================================
#
# Best-effort glue between the practice lifecycle (practices/service.py,
# practices/cancel_service.py) and the Zoom API (zoom_client.py). Every
# function here NEVER RAISES -- a Zoom failure is caught, logged, and
# recorded on the ZoomMeeting row so it stays visible and retryable
# (create failures) or is simply logged (reschedule/delete failures,
# which don't block anything downstream in this step). This is the whole
# point: publish/reschedule/cancel must never be blocked by a third party
# (E21 plan sec 2, confirmed as the intended reading in ПРОМТ №519).
#
# SESSION RULES: no session.commit() here (P-01, same convention as every
# other service module) -- callers manage the transaction. All three
# functions below add/mutate ORM objects on the session passed in; the
# caller's existing commit picks them up.
# =============================================================================

from datetime import UTC

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.practices.models import Practice
from app.modules.zoom.models import ZoomAttendanceSegment, ZoomMeeting, ZoomMeetingStatus, ZoomRegistrant
from app.modules.zoom.zoom_client import (
    ZoomAPIError,
    create_meeting,
    delete_meeting,
    list_registrants,
    patch_meeting,
)

logger = structlog.get_logger()


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

    return row


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
