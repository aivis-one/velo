# =============================================================================
# VELO Backend -- Waitlist Model (Phase 5.3)
# =============================================================================
#
# A waitlist entry ties a user to a full practice's queue.
# When a booking is cancelled, the first waiting user is notified.
#
# STATE MACHINE (enforced in service.py):
#   waiting   -> notified, left
#   notified  -> converted, declined, expired, left
#   converted -> waiting (re-join after booking cancel)
#   left      -> waiting (re-join: UPDATE position + joined_at + status)
#   declined  -> waiting (re-join)
#   expired   -> waiting (re-join)
#
# POSITION:
#   Stored column, computed at INSERT/re-join via subquery:
#   MAX(position) + 1 WHERE practice_id = X. Race-safe because
#   practice is locked with FOR UPDATE during join.
#
# SOFT DELETE:
#   No hard deletes. Leave/decline/expire change status.
#   Re-join updates the same row (UniqueConstraint on practice+user).
#
# EXPIRATION:
#   Periodic task (out of scope Phase 5.3) will transition
#   notified -> expired when expires_at < now(). Lazy check
#   in confirm endpoint as a safety net.
# =============================================================================

import enum
from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.mixins import TimestampMixin, UUIDMixin


class WaitlistStatus(enum.StrEnum):
    """Waitlist entry lifecycle statuses."""

    WAITING = "waiting"
    NOTIFIED = "notified"
    CONVERTED = "converted"
    LEFT = "left"
    DECLINED = "declined"
    EXPIRED = "expired"


# H-02: converted added -- allows re-join after user cancels
# a booking that was created from a waitlist confirmation.
# Without this, converted entries block re-join (not in
# REJOINABLE, not in ACTIVE) and fall through to INSERT
# which hits UniqueConstraint.
REJOINABLE_STATUSES = {
    WaitlistStatus.LEFT.value,
    WaitlistStatus.DECLINED.value,
    WaitlistStatus.EXPIRED.value,
    WaitlistStatus.CONVERTED.value,
}

# Statuses that mean "actively in queue".
ACTIVE_STATUSES = {
    WaitlistStatus.WAITING.value,
    WaitlistStatus.NOTIFIED.value,
}


class Waitlist(UUIDMixin, TimestampMixin, Base):
    """A user's position in the waitlist for a full practice."""

    __tablename__ = "waitlist"

    # -- References --
    practice_id: Mapped[UUID] = mapped_column(
        ForeignKey("practices.id", ondelete="CASCADE"),
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
    )

    # -- Queue position (per-practice, computed at insert/re-join) --
    position: Mapped[int] = mapped_column(Integer)

    # -- Status --
    status: Mapped[str] = mapped_column(
        String(20),
        default=WaitlistStatus.WAITING.value,
        server_default=WaitlistStatus.WAITING.value,
    )

    # -- Timestamps specific to waitlist flow --
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )
    notified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None,
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None,
    )

    __table_args__ = (
        UniqueConstraint(
            "practice_id",
            "user_id",
            name="uq_waitlist_practice_user",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Waitlist id={self.id} practice={self.practice_id} "
            f"user={self.user_id} pos={self.position} "
            f"status={self.status}>"
        )
