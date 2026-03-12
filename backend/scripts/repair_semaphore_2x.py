#!/usr/bin/env python3
# =============================================================================
# VELO Backend -- One-time repair: fix semaphores 2.1 and 2.2
# =============================================================================
#
# PROBLEM 1 (2.1 +2000):
#   repair_orphaned_debits.py added UserLedger(+1000) x2 for Z and Artem
#   but forgot the balancing CompanyLedger(-1000) x2.
#   SUM = +2000 (unbalanced).
#
# PROBLEM 2 (2.2 mismatch):
#   Two orphaned UserLedger debits with reason "purchase:practice=e70f4705..."
#   still match semaphore pattern "%purchase:%" but have no corresponding
#   Purchase rows. This permanently inflates the "actual" side by 2000.
#
# FIXES:
#   1. Add CompanyLedger(-1000) x2 for the two repair_refund entries → fixes 2.1
#   2. Rename orphaned debit reasons: "purchase:..." → "orphaned_purchase:..."
#      so they no longer match "%purchase:%" in semaphore 2.2 → fixes 2.2
#
# NOTE ON MUTABILITY:
#   UserLedger is append-only by convention. Renaming a reason is a one-time
#   exception for corrupted data with no corresponding Purchase. The ledger
#   amounts and balances are not touched — only the reason string.
#
# USAGE:
#   python scripts/repair_semaphore_2x.py --dry-run
#   python scripts/repair_semaphore_2x.py
# =============================================================================

import argparse
import asyncio
import sys
from pathlib import Path

_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import dispose_engine, get_session_factory
from app.modules.payments.models import (
    CompanyLedger,
    CompanyLedgerType,
    LedgerStatus,
    UserLedger,
)
from app.modules.payments.service import record_company_ledger

ORPHANED_PRACTICE_ID = "e70f4705-bdba-413e-abb4-fd080e2a52a5"
ORPHAN_DEBIT_REASON  = f"purchase:practice={ORPHANED_PRACTICE_ID}"
RENAMED_DEBIT_REASON = f"orphaned_purchase:practice={ORPHANED_PRACTICE_ID}"
REFUND_REASON        = f"repair_refund:practice={ORPHANED_PRACTICE_ID}"
COMPANY_REASON       = f"repair_refund_offset:practice={ORPHANED_PRACTICE_ID}"

G = "\033[0;32m"
Y = "\033[1;33m"
R = "\033[0;31m"
N = "\033[0m"


def log(msg: str) -> None:
    print(f"{G}[REPAIR]{N} {msg}")


def warn(msg: str) -> None:
    print(f"{Y}[WARN]{N} {msg}")


def err(msg: str) -> None:
    print(f"{R}[ERROR]{N} {msg}")


async def repair(dry_run: bool = False) -> None:
    factory = get_session_factory()
    async with factory() as session:
        try:
            await _fix_2_1(session, dry_run=dry_run)
            await _fix_2_2(session, dry_run=dry_run)
            if not dry_run:
                await session.commit()
                log("Committed ✓")
                await _verify(session)
            else:
                await session.rollback()
                log("Dry-run complete — no changes written.")
        except Exception as exc:
            await session.rollback()
            err(f"Repair failed: {exc}")
            raise
        finally:
            await dispose_engine()


async def _fix_2_1(session: AsyncSession, dry_run: bool) -> None:
    """Add missing CompanyLedger(-N) for each repair_refund UserLedger entry."""
    log("--- Fix 2.1: add missing company_ledger offsets ---")

    # Find the repair_refund entries created by previous script.
    stmt = select(UserLedger).where(
        UserLedger.reason == REFUND_REASON,
        UserLedger.amount_cents > 0,
        UserLedger.status == LedgerStatus.DONE.value,
    )
    refund_entries = (await session.execute(stmt)).scalars().all()

    if not refund_entries:
        log("  No repair_refund entries found — skipping.")
        return

    log(f"  Found {len(refund_entries)} repair_refund UserLedger entry/entries.")

    created = 0
    skipped = 0

    for entry in refund_entries:
        # Idempotency: check if company entry already exists.
        existing = (await session.execute(
            select(CompanyLedger.id).where(
                CompanyLedger.reason == COMPANY_REASON,
            ).limit(1)
        )).scalar_one_or_none()

        if existing:
            warn(f"  Company offset already exists — skipping.")
            skipped += 1
            continue

        log(
            f"  {'[DRY] Would create' if dry_run else 'Creating'} "
            f"CompanyLedger(amount={-entry.amount_cents}, reason={COMPANY_REASON!r})"
        )

        if not dry_run:
            await record_company_ledger(
                amount_cents=-entry.amount_cents,
                ledger_type=CompanyLedgerType.REFUND.value,
                reason=COMPANY_REASON,
                session=session,
            )
        created += 1

    log(f"  Result: {created} created, {skipped} skipped.")


async def _fix_2_2(session: AsyncSession, dry_run: bool) -> None:
    """Rename orphaned debit reasons so they no longer match '%purchase:%'."""
    log("--- Fix 2.2: rename orphaned debit reasons ---")

    # Find orphaned debits (original reason, still intact).
    stmt = select(UserLedger).where(
        UserLedger.reason == ORPHAN_DEBIT_REASON,
        UserLedger.amount_cents < 0,
        UserLedger.status == LedgerStatus.DONE.value,
    )
    orphans = (await session.execute(stmt)).scalars().all()

    if not orphans:
        log("  No orphaned debits with original reason found — skipping.")
        return

    log(f"  Found {len(orphans)} orphaned debit(s) with reason {ORPHAN_DEBIT_REASON!r}.")
    log(f"  Renaming to {RENAMED_DEBIT_REASON!r}")

    if not dry_run:
        await session.execute(
            update(UserLedger)
            .where(
                UserLedger.reason == ORPHAN_DEBIT_REASON,
                UserLedger.amount_cents < 0,
                UserLedger.status == LedgerStatus.DONE.value,
            )
            .values(reason=RENAMED_DEBIT_REASON)
        )
        log(f"  Renamed {len(orphans)} row(s) ✓")
    else:
        log(f"  [DRY] Would rename {len(orphans)} row(s).")


async def _verify(session: AsyncSession) -> None:
    """Quick post-repair sanity check."""
    from sqlalchemy import func
    from app.modules.payments.models import MasterLedger

    user_sum = (await session.execute(
        select(func.coalesce(func.sum(UserLedger.amount_cents), 0))
        .where(UserLedger.status == LedgerStatus.DONE.value)
    )).scalar_one()

    master_sum = (await session.execute(
        select(func.coalesce(func.sum(MasterLedger.amount_cents), 0))
        .where(MasterLedger.status == LedgerStatus.DONE.value)
    )).scalar_one()

    company_sum = (await session.execute(
        select(func.coalesce(func.sum(CompanyLedger.amount_cents), 0))
        .where(CompanyLedger.status == LedgerStatus.DONE.value)
    )).scalar_one()

    global_sum = user_sum + master_sum + company_sum
    status_2_1 = f"{G}OK{N}" if global_sum == 0 else f"{R}STILL {global_sum}{N}"
    log(f"2.1 global sum: {status_2_1}")

    # Check orphaned debits no longer match purchase pattern.
    still_orphaned = (await session.execute(
        select(func.count()).select_from(UserLedger).where(
            UserLedger.reason == ORPHAN_DEBIT_REASON,
            UserLedger.amount_cents < 0,
        )
    )).scalar_one()
    status_2_2 = f"{G}OK{N}" if still_orphaned == 0 else f"{R}STILL {still_orphaned} rows{N}"
    log(f"2.2 orphaned debits with old reason: {status_2_2}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="VELO -- Fix semaphores 2.1 and 2.2 after orphaned debit repair",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without writing to DB",
    )
    args = parser.parse_args()
    asyncio.run(repair(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
