# =============================================================================
# VELO Backend -- Promo Models (Phase 6.7)
# =============================================================================
#
# Two types of promotional codes:
#
# COMPANY PROMO (type="company"):
#   Created by admin. Company pays for the discount from marketing budget.
#   Master receives full price (company_ledger covers the gap).
#   Commission = 15% of what user actually paid (live money).
#
# MASTER PROMO (type="master"):
#   Created by master. Master gives up part (or all) of their revenue.
#   Company pays nothing. Commission = 15% of what user actually paid.
#
# ALLOWED DISCOUNTS:
#   Both types: [5, 25, 50, 75, 100] percent (from settings).
#
# RACE CONDITION (P-07):
#   used_count incremented atomically via UPDATE ... WHERE used_count < max_uses
#   (not read-then-write). See promos/validation.py (Batch 4).
#
# SOFT DELETE:
#   is_active=False instead of DELETE. Existing purchases keep promo_id FK.
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
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.mixins import TimestampMixin, UUIDMixin


class PromoType(enum.StrEnum):
    """Promo ownership type -- determines who pays for the discount."""

    COMPANY = "company"
    MASTER = "master"


class Promo(UUIDMixin, TimestampMixin, Base):
    """Promotional code for practice discounts.

    company: admin creates, company_ledger pays marketing cost.
    master:  master creates, master absorbs the discount.
    """

    __tablename__ = "promos"

    # -- Code (unique, case-insensitive lookup in service layer) --
    code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False,
    )

    # -- Type --
    type: Mapped[str] = mapped_column(
        String(20), nullable=False,
    )

    # -- Owner (master promos only) --
    master_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )

    # -- Scope (nullable = all practices of the master / all platform) --
    practice_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("practices.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )

    # -- Discount --
    discount_percent: Mapped[int] = mapped_column(
        Integer, nullable=False,
    )

    # -- Usage limits --
    max_uses: Mapped[int | None] = mapped_column(
        Integer, nullable=True,
    )
    used_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0",
    )

    # -- Validity window --
    valid_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
    )
    valid_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )

    # -- Flags --
    first_purchase_only: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true",
    )

    def __repr__(self) -> str:
        return (
            f"<Promo code={self.code!r} type={self.type} "
            f"discount={self.discount_percent}% "
            f"used={self.used_count}/{self.max_uses}>"
        )
