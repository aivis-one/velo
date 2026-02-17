# =============================================================================
# VELO Backend -- Booking Model (Phase 5.1)
# =============================================================================
#
# A booking ties a user to a practice session.
#
# STATE MACHINE (enforced in service.py):
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
#   purchase_id FK -> purchases.id (added Phase 6.4).
#
# ATTENDANCE:
#   joined_at / left_at included for Phase 5.4 (attendance tracking).
#
# UNIQUE INDEX (H-02):
#   Partial unique index on (practice_id, user_id) WHERE status != 'cancelled'.
#   This allows re-booking after cancellation while preventing duplicate
#   active bookings. Old absolute UniqueConstraint blocked re-booking.
#
# INDEXES (R-07):
#   practice_id and user_id have individual B-tree indexes for:
#   - COUNT(bookings) WHERE practice_id=X (capacity check, every booking)
#   - SELECT bookings WHERE user_id=X (GET /bookings/me)
#   The partial unique index does NOT cover single-column lookups.
# =============================================================================

import enum
from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    text,
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
    # R-07: index=True for capacity check (COUNT WHERE practice_id=X).
    practice_id: Mapped[UUID] = mapped_column(
        ForeignKey("practices.id", ondelete="CASCADE"),
        index=True,
    )
    # R-07: index=True for user's booking list (GET /bookings/me).
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )

    # -- Status --
    status: Mapped[str] = mapped_column(
        String(20),
        default=BookingStatus.PENDING.value,
        server_default=BookingStatus.PENDING.value,
    )

    # -- Purchase --
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

    # H-02: partial unique index -- prevents duplicate active bookings
    # but allows re-booking after cancellation.
    __table_args__ = (
        Index(
            "uq_booking_practice_user_active",
            "practice_id",
            "user_id",
            unique=True,
            postgresql_where=text("status != 'cancelled'"),
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Booking id={self.id} practice={self.practice_id} "
            f"user={self.user_id} status={self.status}>"
        )
