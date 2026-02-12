# =============================================================================
# VELO Backend -- Booking Model (Phase 5.1)
# =============================================================================
#
# A booking ties a user to a practice session.
#
# STATE MACHINE (enforced in service.py):
#   pending   -> confirmed, cancelled
#   confirmed -> attended, no_show, cancelled
#   attended  -> (terminal)
#   no_show   -> (terminal)
#   cancelled -> (terminal)
#
# CAPACITY:
#   Checked via COUNT of active bookings (not current_participants).
#   See TD-034.
#
# PURCHASE:
#   purchase_id is a stub column (no FK). Will reference purchases
#   table in Phase 6.4.
#
# ATTENDANCE:
#   joined_at / left_at included for Phase 5.4 (attendance tracking).
# =============================================================================

import enum
from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.mixins import TimestampMixin, UUIDMixin


class BookingStatus(enum.StrEnum):
    """Booking lifecycle statuses."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    ATTENDED = "attended"
    NO_SHOW = "no_show"
    CANCELLED = "cancelled"


class Booking(UUIDMixin, TimestampMixin, Base):
    """A user's booking for a practice session."""

    __tablename__ = "bookings"

    # -- References --
    practice_id: Mapped[UUID] = mapped_column(
        ForeignKey("practices.id", ondelete="CASCADE"),
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
    )

    # -- Status --
    status: Mapped[str] = mapped_column(
        String(20),
        default=BookingStatus.PENDING.value,
        server_default=BookingStatus.PENDING.value,
    )

    # -- Purchase (stub, no FK until Phase 6.4) --
    purchase_id: Mapped[UUID | None] = mapped_column(
        default=None,
    )

    # -- Cancellation --
    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None,
    )
    cancellation_reason: Mapped[str | None] = mapped_column(
        Text, default=None,
    )

    # -- Attendance (Phase 5.4) --
    joined_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None,
    )
    left_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None,
    )

    __table_args__ = (
        UniqueConstraint(
            "practice_id",
            "user_id",
            name="uq_booking_practice_user",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Booking id={self.id} practice={self.practice_id} "
            f"user={self.user_id} status={self.status}>"
        )
