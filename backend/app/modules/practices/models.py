# =============================================================================
# VELO Backend -- Practice Model (Phase 4.1 + 4.3/4.4 pricing)
# =============================================================================
#
# A wellness practice session created by a verified master.
# One master can have many practices. Users book practices in Phase 5.
#
# STATE MACHINE (enforced in service.py):
#   draft      -> scheduled, deleted       (via PATCH)
#   scheduled  -> live                     (via PATCH)
#   scheduled  -> cancelled                (via cancel_practice() ONLY)
#   live       -> completed                (via PATCH)
#   live       -> cancelled                (via cancel_practice() ONLY)
#   completed  -> (terminal)
#   cancelled  -> (terminal)
#   deleted    -> (terminal)
#
# Phase 6.5: scheduled/live -> cancelled is NOT allowed via PATCH status.
# The ONLY path to cancelled is cancel_practice() which handles refunds.
#
# PRICING (Phase 4.3/4.4):
#   is_free=True  -> price_cents MUST be 0 (enforced in service)
#   is_free=False -> price_cents MUST be > 0 (enforced in service)
#   currency defaults to EUR for MVP.
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
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.mixins import TimestampMixin, UUIDMixin


class PracticeType(enum.StrEnum):
    """Types of practices a master can create."""

    LIVE = "live"
    SERIES = "series"
    ONE_ON_ONE = "one_on_one"
    REPLAY = "replay"


class PracticeStatus(enum.StrEnum):
    """Practice lifecycle statuses."""

    DRAFT = "draft"
    SCHEDULED = "scheduled"
    LIVE = "live"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DELETED = "deleted"


class Practice(UUIDMixin, TimestampMixin, Base):
    """A wellness practice session created by a verified master.

    One master can have many practices. Users book practices in Phase 5.
    """

    __tablename__ = "practices"

    # -- Owner --
    # R-07: index=True synced with existing ix_practices_master_id in DB.
    master_id: Mapped[UUID] = mapped_column(
        ForeignKey("master_profiles.user_id", ondelete="CASCADE"),
        index=True,
    )

    # -- Core fields --
    practice_type: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(
        String(20),
        default=PracticeStatus.DRAFT.value,
        server_default=PracticeStatus.DRAFT.value,
    )

    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(
        Text, default=None,
    )

    # -- Scheduling --
    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )
    duration_minutes: Mapped[int] = mapped_column(Integer)
    timezone: Mapped[str] = mapped_column(String(50))

    # -- Capacity --
    max_participants: Mapped[int | None] = mapped_column(
        Integer, default=None,
    )
    # Cached counter -- updated by recalculate_participants() after
    # booking status changes. Capacity checks use COUNT(bookings);
    # this field is for display in PracticeResponse (TD-034).
    current_participants: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
    )

    # -- Pricing (Phase 4.3/4.4) --
    is_free: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
    )
    price_cents: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        default="EUR",
        server_default="EUR",
    )

    # -- Zoom (manual for MVP) --
    zoom_link: Mapped[str | None] = mapped_column(
        String(500), default=None,
    )

    # -- Series support (self-referential FK) --
    parent_practice_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("practices.id", ondelete="SET NULL"),
        default=None,
    )

    def __repr__(self) -> str:
        return (
            f"<Practice id={self.id} type={self.practice_type} "
            f"status={self.status} title={self.title!r} "
            f"is_free={self.is_free} price_cents={self.price_cents}>"
        )
