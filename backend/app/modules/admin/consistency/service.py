# =============================================================================
# VELO Backend -- Admin Consistency Service (Phase 6.8, updated Phase 9)
# =============================================================================
#
# Data consistency semaphores -- 22 checks across 5 categories.
# All queries use pure ORM (no raw SQL). Session is read-only.
#
# CATEGORIES:
#   1. COUNT = COUNT   (1.1 -- 1.4)  Cross-table row count parity.
#   2. SUM = 0         (2.1 -- 2.2)  Double-entry accounting invariant.
#   3. COMPUTED = ACTUAL (3.1 -- 3.5) Cached values match recalculated.
#   4. ORPHAN DETECTION (4.1 -- 4.5) FK integrity beyond DB constraints.
#   5. BUSINESS INVARIANTS (5.1 -- 5.6) Domain rules.
#
# ALERTING:
#   structlog only.
#
# SESSION RULES:
#   Read-only (get_db_reader). No mutations, no commit.
# =============================================================================

from datetime import datetime, timezone

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import AuditLog
from app.modules.admin.consistency.schemas import (
    ConsistencyResponse,
    SemaphoreResult,
)
from app.modules.bookings.models import Booking, BookingStatus
from app.modules.masters.models import MasterProfile
from app.modules.notifications.models import Notification, NotificationDelivery
from app.modules.payments.models import (
    CompanyLedger,
    LedgerStatus,
    MasterLedger,
    Purchase,
    PurchaseStatus,
    UserLedger,
)
from app.modules.practices.models import Practice, PracticeStatus
from app.modules.promos.models import Promo
from app.modules.users.models import User, UserRole

logger = structlog.get_logger()

# Booking statuses that are "active" (not cancelled).
_ACTIVE_BOOKING_STATUSES = {
    BookingStatus.PENDING.value,
    BookingStatus.CONFIRMED.value,
    BookingStatus.ATTENDED.value,
    BookingStatus.NO_SHOW.value,
}

# Booking statuses that count toward current_participants.
_PARTICIPANT_STATUSES = {
    BookingStatus.CONFIRMED.value,
    BookingStatus.ATTENDED.value,
}


# ===================================================================
# Category 1: COUNT = COUNT
# ===================================================================


async def _check_count_count(
    session: AsyncSession,
) -> list[SemaphoreResult]:
    """Cross-table row count parity checks."""
    results: list[SemaphoreResult] = []

    # 1.1: Active bookings == active purchases.
    active_bookings_stmt = select(func.count(Booking.id)).where(
        Booking.status.in_(_ACTIVE_BOOKING_STATUSES),
    )
    active_purchases_stmt = select(func.count(Purchase.id)).where(
        Purchase.status.in_({
            PurchaseStatus.PENDING.value,
            PurchaseStatus.COMPLETED.value,
        }),
    )
    active_bookings = (await session.execute(active_bookings_stmt)).scalar_one()
    active_purchases = (await session.execute(active_purchases_stmt)).scalar_one()
    results.append(SemaphoreResult(
        name="1.1_active_bookings_eq_active_purchases",
        category="count_count",
        status="OK" if active_bookings == active_purchases else "ALERT",
        expected=str(active_bookings),
        actual=str(active_purchases),
        details={"active_bookings": active_bookings, "active_purchases": active_purchases},
        criticality="critical",
    ))

    # 1.2: Cancelled bookings == cancelled/refunded purchases.
    cancelled_bookings_stmt = select(func.count(Booking.id)).where(
        Booking.status == BookingStatus.CANCELLED.value,
    )
    cancelled_purchases_stmt = select(func.count(Purchase.id)).where(
        Purchase.status.in_({
            PurchaseStatus.REFUNDED.value,
            PurchaseStatus.CANCELLED.value,
        }),
    )
    cancelled_bookings = (await session.execute(cancelled_bookings_stmt)).scalar_one()
    cancelled_purchases = (await session.execute(cancelled_purchases_stmt)).scalar_one()
    results.append(SemaphoreResult(
        name="1.2_cancelled_bookings_eq_cancelled_purchases",
        category="count_count",
        status="OK" if cancelled_bookings == cancelled_purchases else "ALERT",
        expected=str(cancelled_bookings),
        actual=str(cancelled_purchases),
        details={
            "cancelled_bookings": cancelled_bookings,
            "cancelled_purchases": cancelled_purchases,
        },
        criticality="critical",
    ))

    # 1.3: Users with role=master == master_profiles rows.
    master_users_stmt = select(func.count(User.id)).where(
        User.role == UserRole.MASTER,
    )
    master_profiles_stmt = select(func.count(MasterProfile.user_id)).where(
        MasterProfile.data["account"]["status"].as_string() == "verified",
    )
    master_users = (await session.execute(master_users_stmt)).scalar_one()
    master_profiles = (await session.execute(master_profiles_stmt)).scalar_one()
    results.append(SemaphoreResult(
        name="1.3_master_users_eq_verified_profiles",
        category="count_count",
        status="OK" if master_users == master_profiles else "ALERT",
        expected=str(master_users),
        actual=str(master_profiles),
        details={"master_users": master_users, "verified_profiles": master_profiles},
        criticality="warning",
    ))

    # 1.4: Every booking has exactly one purchase (1:1).
    # Count bookings that have NO purchase_id set (excluding very new pending).
    bookings_without_purchase_stmt = select(func.count(Booking.id)).where(
        Booking.purchase_id.is_(None),
    )
    orphan_bookings = (await session.execute(bookings_without_purchase_stmt)).scalar_one()
    results.append(SemaphoreResult(
        name="1.4_bookings_all_have_purchase",
        category="count_count",
        status="OK" if orphan_bookings == 0 else "ALERT",
        expected="0",
        actual=str(orphan_bookings),
        details={"bookings_without_purchase": orphan_bookings},
        criticality="critical",
    ))

    return results


# ===================================================================
# Category 2: SUM = 0 (Double-Entry)
# ===================================================================


async def _check_sum_zero(
    session: AsyncSession,
) -> list[SemaphoreResult]:
    """Double-entry accounting invariant checks."""
    results: list[SemaphoreResult] = []

    # 2.1: Global SUM(user_ledger + master_ledger + company_ledger) == 0.
    user_sum_stmt = select(
        func.coalesce(func.sum(UserLedger.amount_cents), 0),
    ).where(UserLedger.status == LedgerStatus.DONE.value)
    master_sum_stmt = select(
        func.coalesce(func.sum(MasterLedger.amount_cents), 0),
    ).where(MasterLedger.status == LedgerStatus.DONE.value)
    company_sum_stmt = select(
        func.coalesce(func.sum(CompanyLedger.amount_cents), 0),
    ).where(CompanyLedger.status == LedgerStatus.DONE.value)

    user_sum = (await session.execute(user_sum_stmt)).scalar_one()
    master_sum = (await session.execute(master_sum_stmt)).scalar_one()
    company_sum = (await session.execute(company_sum_stmt)).scalar_one()
    global_sum = user_sum + master_sum + company_sum

    results.append(SemaphoreResult(
        name="2.1_global_double_entry_sum_zero",
        category="sum_zero",
        status="OK" if global_sum == 0 else "ALERT",
        expected="0",
        actual=str(global_sum),
        details={
            "user_ledger_sum": user_sum,
            "master_ledger_sum": master_sum,
            "company_ledger_sum": company_sum,
        },
        criticality="critical",
    ))

    # 2.2: Per-practice balance via Purchase chain.
    # For each completed practice: SUM of related ledger entries == 0.
    # We check via purchases linked to practices.
    #
    # Approach: for each purchase, the net flow must be:
    #   user_debit + master_credit + company_marketing + company_commission == 0
    # Instead of checking per-practice (complex), we verify the global
    # sum is zero (2.1) and spot-check: total purchase paid_cents ==
    # ABS(user_ledger debits for purchases).
    #
    # Simplified check: total paid_cents across all non-cancelled purchases
    # should equal ABS(SUM of negative user_ledger entries with "purchase:" reason).
    total_paid_stmt = select(
        func.coalesce(func.sum(Purchase.paid_cents), 0),
    ).where(
        Purchase.status.in_({
            PurchaseStatus.PENDING.value,
            PurchaseStatus.COMPLETED.value,
            PurchaseStatus.REFUNDED.value,
        }),
    )
    total_paid = (await session.execute(total_paid_stmt)).scalar_one()

    # User debits for purchases (negative entries with "purchase:" reason).
    user_purchase_debits_stmt = select(
        func.coalesce(func.sum(func.abs(UserLedger.amount_cents)), 0),
    ).where(
        UserLedger.status == LedgerStatus.DONE.value,
        UserLedger.amount_cents < 0,
        UserLedger.reason.like("purchase:%"),
    )
    user_purchase_debits = (await session.execute(user_purchase_debits_stmt)).scalar_one()

    results.append(SemaphoreResult(
        name="2.2_purchase_paid_eq_user_debits",
        category="sum_zero",
        status="OK" if total_paid == user_purchase_debits else "ALERT",
        expected=str(total_paid),
        actual=str(user_purchase_debits),
        details={
            "total_paid_cents": total_paid,
            "user_purchase_debits": user_purchase_debits,
        },
        criticality="critical",
    ))

    return results


# ===================================================================
# Category 3: COMPUTED = ACTUAL (cached balance checks)
# ===================================================================


async def _check_computed_actual(
    session: AsyncSession,
) -> list[SemaphoreResult]:
    """Cached value vs recalculated value checks."""
    results: list[SemaphoreResult] = []

    # -- 3.1: User.balance_cents == SUM(user_ledger WHERE status=done) --
    # Subquery: per-user ledger sum.
    user_ledger_sum = (
        select(
            UserLedger.user_id,
            func.coalesce(func.sum(UserLedger.amount_cents), 0).label("computed"),
        )
        .where(UserLedger.status == LedgerStatus.DONE.value)
        .group_by(UserLedger.user_id)
        .subquery()
    )
    # Join with users who have ledger entries.
    mismatch_3_1_stmt = (
        select(func.count())
        .select_from(User)
        .join(user_ledger_sum, User.id == user_ledger_sum.c.user_id)
        .where(User.balance_cents != user_ledger_sum.c.computed)
    )
    mismatched_users = (await session.execute(mismatch_3_1_stmt)).scalar_one()

    # Also check users with balance_cents != 0 but no ledger entries at all.
    stale_balance_stmt = (
        select(func.count())
        .select_from(User)
        .where(
            User.balance_cents != 0,
            ~User.id.in_(
                select(user_ledger_sum.c.user_id)
            ),
        )
    )
    stale_balance = (await session.execute(stale_balance_stmt)).scalar_one()
    total_user_mismatch = mismatched_users + stale_balance

    results.append(SemaphoreResult(
        name="3.1_user_balance_eq_ledger_sum",
        category="computed_actual",
        status="OK" if total_user_mismatch == 0 else "ALERT",
        expected="0",
        actual=str(total_user_mismatch),
        details={
            "mismatched_with_ledger": mismatched_users,
            "stale_nonzero_without_ledger": stale_balance,
        },
        criticality="critical",
    ))

    # -- 3.2: MasterProfile.frozen_cents == SUM(master_ledger WHERE frozen AND done) --
    frozen_sum = (
        select(
            MasterLedger.user_id,
            func.coalesce(func.sum(MasterLedger.amount_cents), 0).label("computed"),
        )
        .where(
            MasterLedger.status == LedgerStatus.DONE.value,
            MasterLedger.is_frozen.is_(True),
        )
        .group_by(MasterLedger.user_id)
        .subquery()
    )
    mismatch_3_2_stmt = (
        select(func.count())
        .select_from(MasterProfile)
        .join(frozen_sum, MasterProfile.user_id == frozen_sum.c.user_id)
        .where(MasterProfile.frozen_cents != frozen_sum.c.computed)
    )
    mismatched_frozen = (await session.execute(mismatch_3_2_stmt)).scalar_one()

    # Also check masters with frozen_cents != 0 but no frozen ledger entries.
    stale_frozen_stmt = (
        select(func.count())
        .select_from(MasterProfile)
        .where(
            MasterProfile.frozen_cents != 0,
            ~MasterProfile.user_id.in_(
                select(frozen_sum.c.user_id)
            ),
        )
    )
    stale_frozen = (await session.execute(stale_frozen_stmt)).scalar_one()
    total_frozen_mismatch = mismatched_frozen + stale_frozen

    results.append(SemaphoreResult(
        name="3.2_master_frozen_eq_ledger_sum",
        category="computed_actual",
        status="OK" if total_frozen_mismatch == 0 else "ALERT",
        expected="0",
        actual=str(total_frozen_mismatch),
        details={
            "mismatched_with_ledger": mismatched_frozen,
            "stale_nonzero_without_ledger": stale_frozen,
        },
        criticality="critical",
    ))

    # -- 3.3: MasterProfile.available_cents == SUM(master_ledger WHERE NOT frozen AND done) --
    available_sum = (
        select(
            MasterLedger.user_id,
            func.coalesce(func.sum(MasterLedger.amount_cents), 0).label("computed"),
        )
        .where(
            MasterLedger.status == LedgerStatus.DONE.value,
            MasterLedger.is_frozen.is_(False),
        )
        .group_by(MasterLedger.user_id)
        .subquery()
    )
    mismatch_3_3_stmt = (
        select(func.count())
        .select_from(MasterProfile)
        .join(available_sum, MasterProfile.user_id == available_sum.c.user_id)
        .where(MasterProfile.available_cents != available_sum.c.computed)
    )
    mismatched_available = (await session.execute(mismatch_3_3_stmt)).scalar_one()

    # Also check masters with available_cents != 0 but no available ledger entries.
    stale_available_stmt = (
        select(func.count())
        .select_from(MasterProfile)
        .where(
            MasterProfile.available_cents != 0,
            ~MasterProfile.user_id.in_(
                select(available_sum.c.user_id)
            ),
        )
    )
    stale_available = (await session.execute(stale_available_stmt)).scalar_one()
    total_available_mismatch = mismatched_available + stale_available

    results.append(SemaphoreResult(
        name="3.3_master_available_eq_ledger_sum",
        category="computed_actual",
        status="OK" if total_available_mismatch == 0 else "ALERT",
        expected="0",
        actual=str(total_available_mismatch),
        details={
            "mismatched_with_ledger": mismatched_available,
            "stale_nonzero_without_ledger": stale_available,
        },
        criticality="critical",
    ))

    # -- 3.4: Practice.current_participants == COUNT(bookings WHERE confirmed/attended) --
    participant_count = (
        select(
            Booking.practice_id,
            func.count(Booking.id).label("computed"),
        )
        .where(Booking.status.in_(_PARTICIPANT_STATUSES))
        .group_by(Booking.practice_id)
        .subquery()
    )
    # Practices that have bookings but mismatched current_participants.
    mismatch_3_4_stmt = (
        select(func.count())
        .select_from(Practice)
        .join(participant_count, Practice.id == participant_count.c.practice_id)
        .where(Practice.current_participants != participant_count.c.computed)
    )
    mismatched_participants = (await session.execute(mismatch_3_4_stmt)).scalar_one()

    # Also check practices with 0 bookings but current_participants > 0.
    # These won't appear in the JOIN above because the subquery has no row.
    stale_nonzero_stmt = (
        select(func.count())
        .select_from(Practice)
        .where(
            Practice.current_participants > 0,
            ~Practice.id.in_(
                select(participant_count.c.practice_id)
            ),
        )
    )
    stale_nonzero = (await session.execute(stale_nonzero_stmt)).scalar_one()
    total_mismatched = mismatched_participants + stale_nonzero

    results.append(SemaphoreResult(
        name="3.4_practice_participants_eq_booking_count",
        category="computed_actual",
        status="OK" if total_mismatched == 0 else "ALERT",
        expected="0",
        actual=str(total_mismatched),
        details={
            "mismatched_with_bookings": mismatched_participants,
            "stale_nonzero_without_bookings": stale_nonzero,
        },
        criticality="warning",
    ))

    # -- 3.5: Promo.used_count == COUNT(purchases WHERE promo_id=X AND status != cancelled) --
    purchase_promo_count = (
        select(
            Purchase.promo_id,
            func.count(Purchase.id).label("computed"),
        )
        .where(
            Purchase.promo_id.is_not(None),
            Purchase.status != PurchaseStatus.CANCELLED.value,
        )
        .group_by(Purchase.promo_id)
        .subquery()
    )
    mismatch_3_5_stmt = (
        select(func.count())
        .select_from(Promo)
        .join(purchase_promo_count, Promo.id == purchase_promo_count.c.promo_id)
        .where(Promo.used_count != purchase_promo_count.c.computed)
    )
    mismatched_promos = (await session.execute(mismatch_3_5_stmt)).scalar_one()

    # Also check promos with used_count > 0 but no purchases.
    stale_promo_stmt = (
        select(func.count())
        .select_from(Promo)
        .where(
            Promo.used_count > 0,
            ~Promo.id.in_(
                select(purchase_promo_count.c.promo_id)
            ),
        )
    )
    stale_promos = (await session.execute(stale_promo_stmt)).scalar_one()
    total_promo_mismatch = mismatched_promos + stale_promos

    results.append(SemaphoreResult(
        name="3.5_promo_used_count_eq_purchase_count",
        category="computed_actual",
        status="OK" if total_promo_mismatch == 0 else "ALERT",
        expected="0",
        actual=str(total_promo_mismatch),
        details={
            "mismatched_with_purchases": mismatched_promos,
            "stale_nonzero_without_purchases": stale_promos,
        },
        criticality="warning",
    ))

    return results


# ===================================================================
# Category 4: ORPHAN DETECTION
# ===================================================================


async def _check_orphans(
    session: AsyncSession,
) -> list[SemaphoreResult]:
    """Detect records with broken logical references."""
    results: list[SemaphoreResult] = []

    # 4.1: Bookings referencing non-existent practices.
    orphan_4_1_stmt = (
        select(func.count())
        .select_from(Booking)
        .where(
            ~Booking.practice_id.in_(select(Practice.id))
        )
    )
    orphan_bookings_practice = (await session.execute(orphan_4_1_stmt)).scalar_one()
    results.append(SemaphoreResult(
        name="4.1_bookings_orphan_practice",
        category="orphan_detection",
        status="OK" if orphan_bookings_practice == 0 else "ALERT",
        expected="0",
        actual=str(orphan_bookings_practice),
        criticality="critical",
    ))

    # 4.2: Bookings referencing non-existent users.
    orphan_4_2_stmt = (
        select(func.count())
        .select_from(Booking)
        .where(
            ~Booking.user_id.in_(select(User.id))
        )
    )
    orphan_bookings_user = (await session.execute(orphan_4_2_stmt)).scalar_one()
    results.append(SemaphoreResult(
        name="4.2_bookings_orphan_user",
        category="orphan_detection",
        status="OK" if orphan_bookings_user == 0 else "ALERT",
        expected="0",
        actual=str(orphan_bookings_user),
        criticality="critical",
    ))

    # 4.3: Purchases referencing non-existent users.
    orphan_4_3_stmt = (
        select(func.count())
        .select_from(Purchase)
        .where(
            ~Purchase.user_id.in_(select(User.id))
        )
    )
    orphan_purchases_user = (await session.execute(orphan_4_3_stmt)).scalar_one()
    results.append(SemaphoreResult(
        name="4.3_purchases_orphan_user",
        category="orphan_detection",
        status="OK" if orphan_purchases_user == 0 else "ALERT",
        expected="0",
        actual=str(orphan_purchases_user),
        criticality="critical",
    ))

    # 4.4: Master ledger entries referencing non-existent users.
    orphan_4_4_stmt = (
        select(func.count())
        .select_from(MasterLedger)
        .where(
            ~MasterLedger.user_id.in_(select(User.id))
        )
    )
    orphan_master_ledger = (await session.execute(orphan_4_4_stmt)).scalar_one()
    results.append(SemaphoreResult(
        name="4.4_master_ledger_orphan_user",
        category="orphan_detection",
        status="OK" if orphan_master_ledger == 0 else "ALERT",
        expected="0",
        actual=str(orphan_master_ledger),
        criticality="critical",
    ))

    # 4.5: NotificationDelivery without a parent Notification (Phase 9).
    # The FK has ondelete=CASCADE, so this should always be 0.
    # The semaphore verifies the constraint is enforced correctly.
    orphan_4_5_stmt = (
        select(func.count())
        .select_from(NotificationDelivery)
        .where(
            ~NotificationDelivery.notification_id.in_(select(Notification.id))
        )
    )
    orphan_deliveries = (await session.execute(orphan_4_5_stmt)).scalar_one()
    results.append(SemaphoreResult(
        name="4.5_notification_deliveries_orphan_notification",
        category="orphan_detection",
        status="OK" if orphan_deliveries == 0 else "ALERT",
        expected="0",
        actual=str(orphan_deliveries),
        criticality="critical",
    ))

    return results


# ===================================================================
# Category 5: BUSINESS INVARIANTS
# ===================================================================


async def _check_invariants(
    session: AsyncSession,
) -> list[SemaphoreResult]:
    """Domain-specific business rule checks."""
    results: list[SemaphoreResult] = []

    # 5.1: No frozen master_ledger entries for completed practices.
    # After finalize_purchases(), all entries should be unfrozen.
    frozen_completed_stmt = (
        select(func.count())
        .select_from(MasterLedger)
        .join(Practice, MasterLedger.practice_id == Practice.id)
        .where(
            Practice.status == PracticeStatus.COMPLETED.value,
            MasterLedger.is_frozen.is_(True),
            MasterLedger.status == LedgerStatus.DONE.value,
            MasterLedger.amount_cents > 0,  # Only credits (reversal entries are negative).
        )
    )
    frozen_completed = (await session.execute(frozen_completed_stmt)).scalar_one()
    results.append(SemaphoreResult(
        name="5.1_no_frozen_for_completed_practices",
        category="business_invariants",
        status="OK" if frozen_completed == 0 else "ALERT",
        expected="0",
        actual=str(frozen_completed),
        details={"frozen_entries_for_completed": frozen_completed},
        criticality="critical",
    ))

    # 5.2: No master with negative available_cents.
    neg_available_stmt = (
        select(func.count())
        .select_from(MasterProfile)
        .where(MasterProfile.available_cents < 0)
    )
    neg_available = (await session.execute(neg_available_stmt)).scalar_one()
    results.append(SemaphoreResult(
        name="5.2_no_negative_master_available",
        category="business_invariants",
        status="OK" if neg_available == 0 else "ALERT",
        expected="0",
        actual=str(neg_available),
        details={"masters_with_negative_available": neg_available},
        criticality="critical",
    ))

    # 5.3: No user with negative balance_cents.
    neg_balance_stmt = (
        select(func.count())
        .select_from(User)
        .where(User.balance_cents < 0)
    )
    neg_balance = (await session.execute(neg_balance_stmt)).scalar_one()
    results.append(SemaphoreResult(
        name="5.3_no_negative_user_balance",
        category="business_invariants",
        status="OK" if neg_balance == 0 else "ALERT",
        expected="0",
        actual=str(neg_balance),
        details={"users_with_negative_balance": neg_balance},
        criticality="critical",
    ))

    # 5.4: No bookings with attended status where joined_at < practice.scheduled_at
    # minus a tolerance (e.g., someone joined way before the practice).
    # Simplified: attended bookings must have joined_at set.
    attended_no_join_stmt = (
        select(func.count())
        .select_from(Booking)
        .where(
            Booking.status == BookingStatus.ATTENDED.value,
            Booking.joined_at.is_(None),
        )
    )
    attended_no_join = (await session.execute(attended_no_join_stmt)).scalar_one()
    results.append(SemaphoreResult(
        name="5.4_attended_must_have_joined_at",
        category="business_invariants",
        status="OK" if attended_no_join == 0 else "ALERT",
        expected="0",
        actual=str(attended_no_join),
        details={"attended_without_joined_at": attended_no_join},
        criticality="warning",
    ))

    # 5.5: No practice with current_participants > max_participants.
    over_capacity_stmt = (
        select(func.count())
        .select_from(Practice)
        .where(
            Practice.max_participants.is_not(None),
            Practice.current_participants > Practice.max_participants,
        )
    )
    over_capacity = (await session.execute(over_capacity_stmt)).scalar_one()
    results.append(SemaphoreResult(
        name="5.5_no_over_max_participants",
        category="business_invariants",
        status="OK" if over_capacity == 0 else "ALERT",
        expected="0",
        actual=str(over_capacity),
        details={"practices_over_capacity": over_capacity},
        criticality="warning",
    ))

    # 5.6: Every completed purchase has a purchase_completed audit entry.
    completed_purchases_stmt = select(func.count(Purchase.id)).where(
        Purchase.status == PurchaseStatus.COMPLETED.value,
    )
    completed_purchases = (await session.execute(completed_purchases_stmt)).scalar_one()

    audit_completed_stmt = select(func.count(AuditLog.id)).where(
        AuditLog.event == "purchase_completed",
    )
    audit_completed = (await session.execute(audit_completed_stmt)).scalar_one()

    results.append(SemaphoreResult(
        name="5.6_completed_purchases_have_audit",
        category="business_invariants",
        status="OK" if completed_purchases == audit_completed else "ALERT",
        expected=str(completed_purchases),
        actual=str(audit_completed),
        details={
            "completed_purchases": completed_purchases,
            "audit_entries": audit_completed,
        },
        criticality="warning",
    ))

    return results


# ===================================================================
# Main entry point
# ===================================================================


async def run_all_semaphores(
    session: AsyncSession,
) -> ConsistencyResponse:
    """Execute all 22 data consistency semaphores.

    Returns a ConsistencyResponse with individual results and summary.
    Logs ALERTs via structlog for operational visibility.
    """
    all_results: list[SemaphoreResult] = []

    all_results.extend(await _check_count_count(session))
    all_results.extend(await _check_sum_zero(session))
    all_results.extend(await _check_computed_actual(session))
    all_results.extend(await _check_orphans(session))
    all_results.extend(await _check_invariants(session))

    ok_count = sum(1 for r in all_results if r.status == "OK")
    alert_count = sum(1 for r in all_results if r.status == "ALERT")
    now = datetime.now(timezone.utc)

    # Log summary.
    logger.info(
        "consistency_check_completed",
        total=len(all_results),
        ok=ok_count,
        alerts=alert_count,
    )

    # Log individual ALERTs.
    for result in all_results:
        if result.status == "ALERT":
            logger.warning(
                "consistency_alert",
                semaphore=result.name,
                category=result.category,
                criticality=result.criticality,
                expected=result.expected,
                actual=result.actual,
                details=result.details,
            )

    return ConsistencyResponse(
        items=all_results,
        total=len(all_results),
        ok_count=ok_count,
        alert_count=alert_count,
        run_at=now,
    )
