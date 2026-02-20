# =============================================================================
# VELO Backend -- Withdrawal Model (Phase 6.6)
# =============================================================================
#
# Master withdrawal requests for transferring available earnings to bank.
#
# FLOW:
#   1. Master creates withdrawal (POST /masters/me/withdraw).
#      - Validates available_cents >= amount_cents.
#      - Freezes amount via master_ledger (available -> frozen).
#      - Snapshots payout_details from MasterProfile.data.payout.
#
#   2. Admin approves or rejects (POST /admin/withdrawals/{id}/approve|reject).
#      - Approve: debit frozen, credit company fee, create Payment(OUT).
#      - Reject: unfreeze (frozen -> available reversal).
#
# AMOUNT CONVENTION (TD-033):
#   All amounts in EUR cents (integer). 5000 = EUR 50.00.
#   amount_cents = total requested by master (fee deducted from this).
#   fee_cents = platform fee (company keeps).
#   Master receives: amount_cents - fee_cents.
#
# STATE MACHINE:
#   pending  -> approved, rejected
#   approved -> (terminal)
#   rejected -> (terminal)
#
# CONCURRENCY:
#   Admin endpoints use with_for_update() (P-12) to prevent two admins
#   from processing the same withdrawal simultaneously.
#
# SESSION RULES:
#   No session.commit() in service (P-01). Router calls flush + refresh.
# =============================================================================

import enum
from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.mixins import TimestampMixin, UUIDMixin


class WithdrawalStatus(enum.StrEnum):
    """Withdrawal request lifecycle statuses."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Withdrawal(UUIDMixin, TimestampMixin, Base):
    """Master withdrawal request for transferring earnings to bank.

    One master can have multiple pending withdrawals. Each withdrawal
    freezes the requested amount until admin decision.

    amount_cents includes fee_cents. Master receives
    amount_cents - fee_cents on approval.
    """

    __tablename__ = "withdrawals"
    __table_args__ = (
        CheckConstraint("amount_cents > 0", name="ck_withdrawals_amount_positive"),
        CheckConstraint("fee_cents >= 0", name="ck_withdrawals_fee_non_negative"),
    )

    # -- Owner (master) --
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )

    # -- Amount in EUR cents --
    amount_cents: Mapped[int] = mapped_column(Integer)

    # -- Platform fee in EUR cents --
    fee_cents: Mapped[int] = mapped_column(Integer)

    # -- Currency --
    currency: Mapped[str] = mapped_column(
        String(3),
        default="eur",
        server_default="eur",
    )

    # -- Status --
    status: Mapped[str] = mapped_column(
        String(20),
        default=WithdrawalStatus.PENDING.value,
        server_default=WithdrawalStatus.PENDING.value,
    )

    # -- Payout details snapshot (copied from MasterProfile.data.payout) --
    payout_details: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        server_default="{}",
    )

    # -- Admin decision --
    admin_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        default=None,
    )
    admin_note: Mapped[str | None] = mapped_column(
        Text, default=None,
    )
    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None,
    )
    rejected_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None,
    )

    def __repr__(self) -> str:
        return (
            f"<Withdrawal id={self.id} user={self.user_id} "
            f"amount={self.amount_cents} fee={self.fee_cents} "
            f"status={self.status}>"
        )
