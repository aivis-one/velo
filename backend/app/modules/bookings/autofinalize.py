# =============================================================================
# VELO Backend -- Practice Auto-Finalizer (Batch 1)
# =============================================================================
#
# Background asyncio.Task that runs inside FastAPI lifespan, mirroring the
# notification processor (app/modules/notifications/processor.py).
#
# WHY:
#   A master finalizes a practice by hand ("Закрыть"). If they forget, the
#   practice would stay scheduled/live forever: its confirmed bookings never
#   resolve to attended/no_show, the master's money stays frozen, and the
#   practice keeps haunting the catalog / dashboard. This worker enforces a
#   hard ceiling: any practice that started more than
#   settings.practice_max_duration_hours ago is closed automatically.
#
# HOW:
#   Poll practices WHERE status IN (scheduled, live) AND
#   scheduled_at <= now - ceiling. For each, run the SAME settlement core as
#   the manual path via bookings.service.auto_finalize_practice (attendance +
#   ledger unfreeze/commission + diary projection), acting as the system.
#
# SESSION / ISOLATION:
#   Runs outside request context -- uses get_session_factory() like the
#   notification processor and the Stripe webhook. Unlike the notification
#   processor (which locks and processes a whole batch in one transaction),
#   each practice here is finalized in its OWN session/transaction: settlement
#   touches money + diary and is comparatively heavy, so we isolate failures
#   (one bad practice must not roll back the others) and keep the FOR UPDATE
#   lock held only for that practice's settlement.
#
#   Selection and settlement use FOR UPDATE SKIP LOCKED so a practice a master
#   is finalizing by hand right now (its row already locked) is simply skipped
#   this tick and picked up next time -- no double finalize, no deadlock.
#
# BACKOFF:
#   Empty poll -> interval doubles (up to max_backoff). Work found -> reset.
#
# ERROR HANDLING:
#   Each practice is finalized independently. One failure is logged and the
#   loop continues. Unhandled exceptions in the main loop are caught, logged,
#   and the loop continues after backoff.
# =============================================================================

import asyncio
from datetime import UTC, datetime, timedelta

import structlog
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.database import get_session_factory
from app.core.exceptions import BadRequestError, NotFoundError
from app.modules.bookings.service import auto_finalize_practice
from app.modules.practices.models import Practice, PracticeStatus

logger = structlog.get_logger()

# Practice statuses that can still be (auto-)finalized. Mirrors
# _FINALIZABLE_PRACTICE_STATUSES in bookings/service.py.
_FINALIZABLE_PRACTICE_STATUSES = {
    PracticeStatus.SCHEDULED.value,
    PracticeStatus.LIVE.value,
}

# How many overdue practices to claim per poll cycle.
_BATCH_SIZE = 50


# ===================================================================
# Main loop
# ===================================================================


async def run_autofinalizer() -> None:
    """Main auto-finalizer loop. Runs until cancelled.

    Called from FastAPI lifespan as a background task. Catches all
    exceptions to prevent the loop from dying.
    """
    base_interval = settings.practice_autofinalize_poll_interval_seconds
    max_backoff = settings.practice_autofinalize_max_backoff_seconds
    interval = base_interval

    logger.info(
        "practice_autofinalizer_started",
        poll_interval=base_interval,
        max_backoff=max_backoff,
        max_duration_hours=settings.practice_max_duration_hours,
    )

    while True:
        try:
            work_done = await _poll_cycle()

            if work_done:
                interval = base_interval
            else:
                interval = min(interval * 2, max_backoff)

        except asyncio.CancelledError:
            logger.info("practice_autofinalizer_stopped")
            return
        except Exception:
            logger.exception("practice_autofinalizer_error")
            interval = max_backoff

        try:
            await asyncio.sleep(interval)
        except asyncio.CancelledError:
            logger.info("practice_autofinalizer_stopped")
            return


# ===================================================================
# Poll cycle
# ===================================================================


async def _poll_cycle() -> bool:
    """Claim and finalize overdue practices.

    Returns True if at least one practice was finalized (resets backoff).

    Selection runs in its own short transaction: it locks the overdue rows
    with SKIP LOCKED, collects their ids, and releases immediately. Each id
    is then finalized in a fresh session so a single failure cannot roll back
    the rest of the batch.
    """
    overdue_ids = await _claim_overdue_ids()
    if not overdue_ids:
        return False

    finalized = 0
    for practice_id in overdue_ids:
        if await _finalize_one(practice_id):
            finalized += 1

    if finalized > 0:
        logger.info("practice_autofinalize_batch", finalized=finalized)

    return finalized > 0


async def _claim_overdue_ids() -> list:
    """Return ids of practices past the auto-finalization ceiling.

    A practice is overdue when it is still scheduled/live and its scheduled_at
    is more than practice_max_duration_hours in the past. FOR UPDATE SKIP
    LOCKED means rows currently locked by a manual finalize are skipped this
    tick (picked up next cycle), preventing double finalize and deadlocks.
    """
    factory = get_session_factory()
    cutoff = datetime.now(UTC) - timedelta(
        hours=settings.practice_max_duration_hours,
    )

    try:
        async with factory() as session:
            stmt = (
                select(Practice.id)
                .where(
                    Practice.status.in_(_FINALIZABLE_PRACTICE_STATUSES),
                    Practice.scheduled_at <= cutoff,
                )
                .order_by(Practice.scheduled_at.asc())
                .limit(_BATCH_SIZE)
                .with_for_update(skip_locked=True)
            )
            result = await session.execute(stmt)
            ids = list(result.scalars().all())
            # Read-only claim: nothing was mutated, so just let the
            # transaction close (rollback) and release the locks.
            return ids
    except Exception:
        logger.exception("practice_autofinalize_claim_error")
        return []


async def _finalize_one(practice_id) -> bool:
    """Finalize a single practice in its own transaction.

    Returns True on success. Errors are logged and swallowed so the batch
    continues. BadRequestError/NotFoundError are expected races (the practice
    was finalized or removed between claim and settlement) and are logged at
    info, not error.
    """
    factory = get_session_factory()

    try:
        async with factory() as session:
            try:
                await auto_finalize_practice(practice_id, session)
                await session.commit()
                return True
            except (BadRequestError, NotFoundError) as exc:
                # Lost the race (already finalized/removed) -- not an error.
                await session.rollback()
                logger.info(
                    "practice_autofinalize_skipped",
                    practice_id=str(practice_id),
                    reason=str(exc),
                )
                return False
            except IntegrityError:
                await session.rollback()
                logger.exception(
                    "practice_autofinalize_integrity_error",
                    practice_id=str(practice_id),
                )
                return False
    except Exception:
        # Anything else (DB hiccup, settlement bug): log and move on so one
        # bad practice never stalls the worker.
        logger.exception(
            "practice_autofinalize_failed",
            practice_id=str(practice_id),
        )
        return False
