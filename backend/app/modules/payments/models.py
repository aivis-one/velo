# =============================================================================
# VELO Backend — Payment Ledger Models (Phase 6.1)
# =============================================================================
#
# Double-entry bookkeeping: every cent is tracked across three journals.
# Golden rule: SUM(user_ledger + master_ledger + company_ledger) = 0
#
# THREE LEDGERS:
#   UserLedger    — all movements on a user's wallet (topup, purchase, refund)
#   MasterLedger  — all movements on a master's earnings (sale, commission, withdrawal)
#   CompanyLedger — platform revenue (commissions, marketing spend, refunds, fees)
#
# AMOUNT CONVENTION (TD-033):
#   All amounts in EUR cents (integer). 1500 = €15.00.
#   Positive = credit, negative = debit.
#   Matches Practice.price_cents already in use since Phase 4.3.
#
# IMMUTABILITY:
#   Ledger rows are append-only. No updated_at, no UPDATEs.
#   Status transitions (pending → done/cancelled) are the ONLY mutation,
#   handled via UPDATE on the status column only.
#   UUIDMixin used for id. No TimestampMixin (no updated_at needed).
#
# BALANCE CACHE:
#   User.balance_cents           = SUM(user_ledger.amount_cents) WHERE status='done'
#   MasterProfile.frozen_cents   = SUM(master_ledger.amount_cents) WHERE status='done' AND is_frozen=true
#   MasterProfile.available_cents= SUM(master_ledger.amount_cents) WHERE status='done' AND is_frozen=false
#   Updated by listeners (Phase 6.2), NOT by direct writes.
#
# SESSION RULES:
#   No session.commit() in service functions (P-01).
# =============================================================================

import enum
from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.mixins import UUIDMixin


# -- Enums (P-09: StrEnum) --------------------------------------------------


class LedgerStatus(enum.StrEnum):
    """Transaction lifecycle status.

    PENDING:   awaiting external confirmation (e.g. Stripe webhook).
    DONE:      confirmed and included in balance calculations.
    CANCELLED: voided, excluded from balance calculations.
    """

    PENDING = "pending"
    DONE = "done"
    CANCELLED = "cancelled"


class CompanyLedgerType(enum.StrEnum):
    """Types of company ledger entries.

    COMMISSION:     platform fee from completed practices (15%).
    MARKETING:      company-funded promo spending.
    REFUND:         money returned to users from company funds.
    WITHDRAWAL_FEE: fixed fee charged on master withdrawals.
    """

    COMMISSION = "commission"
    MARKETING = "marketing"
    REFUND = "refund"
    WITHDRAWAL_FEE = "withdrawal_fee"


# -- Models ------------------------------------------------------------------


class UserLedger(UUIDMixin, Base):
    """User wallet journal — every movement on a user's balance.

    Positive amount_cents = credit (topup, refund).
    Negative amount_cents = debit (purchase, transfer to master balance).
    """

    __tablename__ = "user_ledger"

    # -- Owner --
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )

    # -- Amount in EUR cents --
    amount_cents: Mapped[int] = mapped_column(Integer)

    # -- Status --
    status: Mapped[str] = mapped_column(
        String(20),
        default=LedgerStatus.DONE.value,
        server_default=LedgerStatus.DONE.value,
    )

    # -- Context --
    reason: Mapped[str] = mapped_column(String(200))
    notes: Mapped[str | None] = mapped_column(Text, default=None)

    # -- Timestamp (immutable, no updated_at) --
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )

    def __repr__(self) -> str:
        return (
            f"<UserLedger id={self.id} user={self.user_id} "
            f"amount={self.amount_cents} status={self.status}>"
        )


class MasterLedger(UUIDMixin, Base):
    """Master earnings journal — every movement on a master's account.

    Tracks both frozen (awaiting practice completion) and available
    (withdrawable) funds separately via is_frozen flag.

    Positive amount_cents = credit (sale).
    Negative amount_cents = debit (commission, withdrawal).
    """

    __tablename__ = "master_ledger"

    # -- Owner --
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )

    # -- Amount in EUR cents --
    amount_cents: Mapped[int] = mapped_column(Integer)

    # -- Frozen flag --
    # True = funds locked until practice completes.
    # False = funds available for withdrawal.
    is_frozen: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
    )

    # -- Status --
    status: Mapped[str] = mapped_column(
        String(20),
        default=LedgerStatus.DONE.value,
        server_default=LedgerStatus.DONE.value,
    )

    # -- Context --
    reason: Mapped[str] = mapped_column(String(200))
    practice_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("practices.id", ondelete="SET NULL"),
        index=True,
        default=None,
    )
    notes: Mapped[str | None] = mapped_column(Text, default=None)

    # -- Timestamp (immutable, no updated_at) --
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )

    def __repr__(self) -> str:
        return (
            f"<MasterLedger id={self.id} user={self.user_id} "
            f"amount={self.amount_cents} frozen={self.is_frozen} "
            f"status={self.status}>"
        )


class CompanyLedger(UUIDMixin, Base):
    """Platform revenue journal — commissions, marketing, refunds, fees.

    No user_id — this is the platform's own account.
    reference_id links back to the purchase/withdrawal that triggered
    this entry for audit trail purposes.
    """

    __tablename__ = "company_ledger"

    # -- Amount in EUR cents --
    amount_cents: Mapped[int] = mapped_column(Integer)

    # -- Type --
    type: Mapped[str] = mapped_column(String(20))

    # -- Status --
    status: Mapped[str] = mapped_column(
        String(20),
        default=LedgerStatus.DONE.value,
        server_default=LedgerStatus.DONE.value,
    )

    # -- Context --
    reason: Mapped[str] = mapped_column(String(200))
    reference_id: Mapped[UUID | None] = mapped_column(
        default=None,
        index=True,
    )

    # -- Timestamp (immutable, no updated_at) --
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )

    def __repr__(self) -> str:
        return (
            f"<CompanyLedger id={self.id} type={self.type} "
            f"amount={self.amount_cents} status={self.status}>"
        )
