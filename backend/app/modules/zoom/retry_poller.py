# =============================================================================
# VELO Backend -- Zoom Meeting Creation Retry Poller (E21 step D)
# =============================================================================
#
# Background asyncio.Task, same shape as run_autofinalizer
# (bookings/autofinalize.py) and run_processor (notifications/processor.py):
# runs inside FastAPI lifespan, per-row isolated try/except so one meeting's
# failure never blocks another, exponential backoff on empty polls.
#
# WHY:
#   Publishing a practice must always succeed even if Zoom is unreachable
#   (E21 plan sec 2) -- so a failed meeting creation is recorded as
#   ZoomMeeting.status=create_failed rather than raised. This worker is what
#   actually retries those rows afterward, capped
#   (settings.zoom_meeting_create_max_retries) so a permanently-broken
#   config doesn't retry forever -- past the cap the row stays VISIBLY
#   create_failed (retry_count + last_sync_error both readable), the poller
#   just stops touching it.
#
# SESSION / ISOLATION:
#   Each row is retried in its OWN session/transaction, claimed with
#   FOR UPDATE SKIP LOCKED so a row already being retried (or edited
#   concurrently) is skipped this tick, not double-processed.
# =============================================================================

import asyncio
from datetime import UTC, datetime

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_session_factory
from app.modules.practices.models import Practice
from app.modules.zoom.models import ZoomMeeting, ZoomMeetingStatus
from app.modules.zoom.zoom_client import ZoomAPIError, create_meeting

logger = structlog.get_logger()


# ===================================================================
# Main loop
# ===================================================================


async def run_zoom_retry_poller() -> None:
    """Main retry-poller loop. Runs until cancelled.

    Called from FastAPI lifespan as a background task. Catches all
    exceptions to prevent the loop from dying.
    """
    base_interval = settings.zoom_retry_poll_interval_seconds
    max_backoff = settings.zoom_retry_max_backoff_seconds
    interval = base_interval

    logger.info(
        "zoom_retry_poller_started",
        poll_interval=base_interval,
        max_backoff=max_backoff,
        max_retries=settings.zoom_meeting_create_max_retries,
    )

    while True:
        try:
            work_done = await _poll_cycle()

            if work_done:
                interval = base_interval
            else:
                interval = min(interval * 2, max_backoff)

        except asyncio.CancelledError:
            logger.info("zoom_retry_poller_stopped")
            return
        except Exception:
            logger.exception("zoom_retry_poller_error")
            interval = max_backoff

        try:
            await asyncio.sleep(interval)
        except asyncio.CancelledError:
            logger.info("zoom_retry_poller_stopped")
            return


# ===================================================================
# Poll cycle
# ===================================================================


async def _poll_cycle() -> bool:
    """Retry every create_failed ZoomMeeting row still under the cap.

    Returns True if at least one row was retried (regardless of outcome --
    a retry that fails again still counts as work done, matching
    run_autofinalizer's "work found resets backoff" semantics).
    """
    ids = await _claim_retryable_ids()
    retried = 0
    for meeting_id in ids:
        if await _retry_one(meeting_id):
            retried += 1
    if retried > 0:
        logger.info("zoom_retry_batch", retried=retried)
    return retried > 0


async def _claim_retryable_ids() -> list:
    """Return ids of ZoomMeeting rows still eligible for a retry attempt."""
    factory = get_session_factory()
    cap = settings.zoom_meeting_create_max_retries

    try:
        async with factory() as session:
            stmt = (
                select(ZoomMeeting.id)
                .where(
                    ZoomMeeting.status == ZoomMeetingStatus.CREATE_FAILED.value,
                    ZoomMeeting.retry_count < cap,
                )
                .order_by(ZoomMeeting.created_at.asc())
                .with_for_update(skip_locked=True)
            )
            result = await session.execute(stmt)
            ids = list(result.scalars().all())
            # Read-only claim: release the SKIP LOCKED locks now rather than
            # holding them until session close.
            await session.rollback()
            return ids
    except Exception:
        logger.exception("zoom_retry_claim_error")
        return []


async def _retry_one(meeting_id) -> bool:
    """Retry meeting creation for one ZoomMeeting row, in its own transaction.

    Returns True whether the retry succeeded or failed (both are "work
    done" for backoff purposes) -- False only on an unexpected error that
    prevented even attempting the retry.
    """
    factory = get_session_factory()

    try:
        async with factory() as session:
            row = (
                await session.execute(
                    select(ZoomMeeting)
                    .where(ZoomMeeting.id == meeting_id)
                    .with_for_update()
                )
            ).scalar_one_or_none()
            if row is None or row.status != ZoomMeetingStatus.CREATE_FAILED.value:
                # Lost the race (already retried/resolved elsewhere).
                await session.rollback()
                return False

            practice = await session.get(Practice, row.practice_id)
            if practice is None:
                # Practice gone -- nothing left to create a meeting for.
                await session.rollback()
                return False

            await _attempt_create(row, practice, session)
            await session.commit()
            return True
    except Exception:
        logger.exception("zoom_retry_failed", meeting_id=str(meeting_id))
        return False


async def _attempt_create(
    row: ZoomMeeting,
    practice: Practice,
    session: AsyncSession,
) -> None:
    """One creation attempt against the Zoom API, updating `row` in place.

    Never raises -- ZoomAPIError (and anything else) is caught and recorded
    as last_sync_error, same posture as the initial attempt in
    practices/service.py. Caller commits.
    """
    row.retry_count += 1
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
        row.last_sync_error = None
        logger.info(
            "zoom_meeting_retry_succeeded",
            practice_id=str(practice.id),
            zoom_meeting_id=row.zoom_meeting_id,
            attempt=row.retry_count,
        )
    except ZoomAPIError as exc:
        at_cap = row.retry_count >= settings.zoom_meeting_create_max_retries
        suffix = " (retry cap reached, no further attempts)" if at_cap else ""
        row.last_sync_error = (
            f"create_meeting retry #{row.retry_count} failed: "
            f"status={exc.status_code} body={exc.body}{suffix}"
        )
        logger.warning(
            "zoom_meeting_retry_failed",
            practice_id=str(practice.id),
            attempt=row.retry_count,
            at_cap=at_cap,
            status_code=exc.status_code,
        )
