#!/usr/bin/env python3
# =============================================================================
# VELO Backend -- One-time repair: refund orphaned purchase debits
# =============================================================================
#
# PROBLEM:
#   Two real users (Z tg=5971989877, Artem tg=526738615) bought a seed
#   practice via normal purchase flow. The purchase reason was recorded as
#   "purchase:practice=e70f4705-..." (not "seed:..."), so when
#   `velo seed --reset` deleted the practice and its purchases, the
#   UserLedger debit entries were NOT cleaned up.
#
#   Result: each user lost 1000 cents with no matching refund or purchase.
#
# WHAT THIS SCRIPT DOES:
#   1. Finds orphaned UserLedger debits for the deleted practice.
#   2. Creates offsetting UserLedger(+1000) refund entry for each user.
#   3. Recalculates balance cache via record_user_ledger (P-07).
#   Idempotent: skips users who already have a matching refund entry.
#
# USAGE:
#   python scripts/repair_orphaned_debits.py --dry-run
#   python scripts/repair_orphaned_debits.py
# =============================================================================

import argparse
import asyncio
import sys
from pathlib import Path

_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import dispose_engine, get_session_factory
from app.modules.payments.models import LedgerStatus, UserLedger
from app.modules.payments.service import record_user_ledger
from app.modules.users.models import User

# The deleted practice UUID.
ORPHANED_PRACTICE_ID = "e70f4705-bdba-413e-abb4-fd080e2a52a5"
ORPHAN_REASON = f"purchase:practice={ORPHANED_PRACTICE_ID}"
REFUND_REASON = f"repair_refund:practice={ORPHANED_PRACTICE_ID}"

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
            await _repair(session, dry_run=dry_run)
            if not dry_run:
                await session.commit()
                log("Committed ✓")
            else:
                await session.rollback()
                log("Dry-run complete — no changes written.")
        except Exception as exc:
            await session.rollback()
            err(f"Repair failed: {exc}")
            raise
        finally:
            await dispose_engine()


async def _repair(session: AsyncSession, dry_run: bool) -> None:
    # Find all orphaned debits for this practice.
    stmt = select(UserLedger).where(
        UserLedger.reason == ORPHAN_REASON,
        UserLedger.amount_cents < 0,
        UserLedger.status == LedgerStatus.DONE.value,
    )
    orphans = (await session.execute(stmt)).scalars().all()

    if not orphans:
        log("No orphaned debits found — nothing to do.")
        return

    log(f"Found {len(orphans)} orphaned debit(s) for practice {ORPHANED_PRACTICE_ID}.")

    refunded = 0
    skipped = 0

    for entry in orphans:
        # Idempotency: check if refund already exists for this user.
        existing = (await session.execute(
            select(UserLedger.id).where(
                UserLedger.user_id == entry.user_id,
                UserLedger.reason == REFUND_REASON,
            ).limit(1)
        )).scalar_one_or_none()

        if existing:
            warn(f"  Skipping user {entry.user_id} — refund already exists.")
            skipped += 1
            continue

        # Load user info for logging.
        user = await session.get(User, entry.user_id)
        tg = user.telegram_id if user else "?"
        name = user.first_name if user else "?"
        amount = abs(entry.amount_cents)

        log(
            f"  {'[DRY] Would refund' if dry_run else 'Refunding'} "
            f"user {name} (tg={tg}): +{amount} cents  [reason={REFUND_REASON!r}]"
        )

        if not dry_run:
            # record_user_ledger recalculates balance cache (P-07).
            await record_user_ledger(
                user_id=entry.user_id,
                amount_cents=amount,
                reason=REFUND_REASON,
                session=session,
                notes=(
                    "Repair refund: seed practice was deleted during seed reset, "
                    "leaving orphaned debit. This entry restores the lost balance."
                ),
            )

        refunded += 1

    log(
        f"\nSummary: {refunded} refund(s) {'would be ' if dry_run else ''}created, "
        f"{skipped} already exist."
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="VELO -- Refund orphaned purchase debits for deleted seed practice",
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
