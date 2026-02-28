# =============================================================================
# VELO Backend -- Diary Models (Phase 8.1: Check-ins, Phase 8.2: Feedbacks)
# =============================================================================
#
# Checkin: user's mood before a practice session.
# Feedback: user's rating after a completed practice.
#
# CHECKIN LIFECYCLE:
#   Window opens: scheduled_at - checkin_window_hours (config).
#   Window closes: scheduled_at.
#   Condition: booking.status == confirmed.
#   Upsert: one checkin per booking, updatable within window.
#
# FEEDBACK LIFECYCLE:
#   Window opens: practice.status == completed (i.e. after completion).
#   Window closes: scheduled_at + duration_minutes + feedback_window_hours.
#   Condition: booking.status == attended.
#   Upsert: one feedback per (practice, user), updatable within window.
#
# CHECK TYPE (rose socket for future post-check-in):
#   "pre"  -- before practice (MVP, the only value used now).
#   "post" -- after practice (future Phase 9+).
#
# UNIQUE CONSTRAINTS:
#   checkins:  (booking_id, check_type) -- one pre and one post per booking.
#   feedbacks: (practice_id, user_id)   -- one feedback per user per practice.
#
# SESSION RULES:
#   No session.commit() in service (P-01). Router manages transaction.
# =============================================================================

import enum

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


class Mood(enum.StrEnum):
    """User mood before (or after) a practice."""

    LOW = "low"
    MID = "mid"
    HIGH = "high"


class CheckType(enum.StrEnum):
    """Check-in timing relative to practice.

    PRE:  before practice (MVP).
    POST: after practice (future rose socket).
    """

    PRE = "pre"
    POST = "post"


class Rating(enum.StrEnum):
    """Feedback rating after a practice."""

    FIRE = "fire"
    GOOD = "good"
    CONFUSED = "confused"


class Checkin(UUIDMixin, TimestampMixin, Base):
    """User's mood check-in linked to a booking.

    One pre-check-in per booking. Updatable within the time window
    (scheduled_at - checkin_window_hours .. scheduled_at).
    """

    __tablename__ = "checkins"

    # -- References --
    practice_id: Mapped[UUID] = mapped_column(
        ForeignKey("practices.id", ondelete="CASCADE"),
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    booking_id: Mapped[UUID] = mapped_column(
        ForeignKey("bookings.id", ondelete="CASCADE"),
        index=True,
    )

    # -- Check-in data --
    mood: Mapped[str] = mapped_column(
        String(10), nullable=False,
    )
    comment: Mapped[str | None] = mapped_column(
        Text, default=None,
    )

    # -- Type (pre/post rose socket) --
    check_type: Mapped[str] = mapped_column(
        String(10),
        default=CheckType.PRE.value,
        server_default=CheckType.PRE.value,
    )

    __table_args__ = (
        UniqueConstraint(
            "booking_id",
            "check_type",
            name="uq_checkin_booking_type",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Checkin id={self.id} booking={self.booking_id} "
            f"mood={self.mood} type={self.check_type}>"
        )


class Feedback(UUIDMixin, TimestampMixin, Base):
    """User's feedback after a completed practice.

    One feedback per user per practice. Updatable within the window
    (practice end .. practice end + feedback_window_hours).
    """

    __tablename__ = "feedbacks"

    # -- References --
    practice_id: Mapped[UUID] = mapped_column(
        ForeignKey("practices.id", ondelete="CASCADE"),
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    booking_id: Mapped[UUID] = mapped_column(
        ForeignKey("bookings.id", ondelete="CASCADE"),
        index=True,
    )

    # -- Feedback data --
    rating: Mapped[str] = mapped_column(
        String(10), nullable=False,
    )
    comment: Mapped[str | None] = mapped_column(
        Text, default=None,
    )

    __table_args__ = (
        UniqueConstraint(
            "practice_id",
            "user_id",
            name="uq_feedback_practice_user",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Feedback id={self.id} practice={self.practice_id} "
            f"user={self.user_id} rating={self.rating}>"
        )
