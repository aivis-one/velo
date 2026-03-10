# =============================================================================
# VELO Backend -- Diary Models (Phase 8.1-8.3)
# =============================================================================
#
# Checkin:    user's mood before a practice session.
# Feedback:   user's rating after a completed practice.
# DiaryEntry: personal journal entry, optionally linked to a practice.
#
# CHECKIN LIFECYCLE:
#   Window opens: scheduled_at - checkin_window_hours (config).
#   Window closes: scheduled_at.
#   Condition: booking.status == confirmed.
#   Upsert: one checkin per booking, updatable within window.
#
# FEEDBACK LIFECYCLE:
#   Window opens: practice.status == completed.
#   Window closes: scheduled_at + duration_minutes + feedback_window_hours.
#   Condition: booking.status == attended.
#   Upsert: one feedback per (practice, user), updatable within window.
#
# DIARY ENTRY:
#   No time window. User can create/edit/delete anytime.
#   Optional link to practice (validated: practice exists + user has booking).
#   Hard delete on DELETE -- personal data, no soft delete.
#
# CHECK CONSTRAINTS (WARNING-9 fix + 11.3 fix):
#   DB-level validation for mood, rating, and check_type columns.
#   Defense-in-depth: Pydantic Literal validates at API level,
#   CheckConstraint validates at DB level for non-API write paths.
#
#   11.3 fix: added ck_checkin_check_type on Checkin.check_type.
#   mood and rating already had constraints; check_type was missing one.
#   Non-API write paths (e.g. seed.py, tests) could insert invalid values
#   without this constraint.
#
# SESSION RULES:
#   No session.commit() in service (P-01). Router manages transaction.
# =============================================================================

import enum

from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
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


# ===================================================================
# Checkin (Phase 8.1)
# ===================================================================


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
        CheckConstraint(
            "mood IN ('low', 'mid', 'high')",
            name="ck_checkin_mood",
        ),
        # 11.3 fix: check_type had no DB-level constraint. Non-API write
        # paths could insert arbitrary strings without detection.
        CheckConstraint(
            "check_type IN ('pre', 'post')",
            name="ck_checkin_check_type",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Checkin id={self.id} booking={self.booking_id} "
            f"mood={self.mood} type={self.check_type}>"
        )


# ===================================================================
# Feedback (Phase 8.2)
# ===================================================================


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
        CheckConstraint(
            "rating IN ('fire', 'good', 'confused')",
            name="ck_feedback_rating",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Feedback id={self.id} practice={self.practice_id} "
            f"user={self.user_id} rating={self.rating}>"
        )


# ===================================================================
# DiaryEntry (Phase 8.3)
# ===================================================================


class DiaryEntry(UUIDMixin, TimestampMixin, Base):
    """Personal journal entry, optionally linked to a practice.

    No time window restrictions. User can create, edit, and delete
    entries at any time. Hard delete on DELETE (personal data).
    """

    __tablename__ = "diary_entries"

    # -- Owner --
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )

    # -- Optional practice link --
    practice_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("practices.id", ondelete="SET NULL"),
        index=True,
        default=None,
    )

    # -- Content --
    title: Mapped[str | None] = mapped_column(
        String(200), default=None,
    )
    content: Mapped[str] = mapped_column(
        Text, nullable=False,
    )
    mood: Mapped[str | None] = mapped_column(
        String(10), default=None,
    )

    __table_args__ = (
        CheckConstraint(
            "mood IS NULL OR mood IN ('low', 'mid', 'high')",
            name="ck_diary_entry_mood",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<DiaryEntry id={self.id} user={self.user_id} "
            f"title={self.title!r} mood={self.mood}>"
        )
