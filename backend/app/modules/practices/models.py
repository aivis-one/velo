# =============================================================================
# VELO Backend -- Practice Model (Phase 4.1)
# =============================================================================
#
# Practices are the core entity of the platform. A verified master creates
# a practice; users browse and book them (Phase 5).
#
# TYPES:
#   live       -- single live session (Zoom)
#   series     -- recurring (linked via parent_practice_id)
#   one_on_one -- private session
#   replay     -- pre-recorded, available on-demand
#
# STATUS MACHINE:
#   draft -> scheduled -> live -> completed
#   draft -> cancelled
#   scheduled -> cancelled
#
# DENORMALIZATION:
#   current_participants is stored but NOT USED until Phase 5.
#   Phase 5 will decide: increment on booking or compute via COUNT.
#   TODO Phase 5: Wire current_participants or remove the column.
#
# NAMING:
#   Column is `practice_type`, not `type` -- avoids shadowing Python builtin.
#   This is a deliberate deviation from the original spec.
#
# FK:
#   master_id -> master_profiles.user_id (not users.id) -- guarantees at DB
#   level that only users with a master profile can own practices.
# =============================================================================

import enum
from datetime import datetime
from uuid import UUID

from sqlalchemy import (
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


class Practice(UUIDMixin, TimestampMixin, Base):
    """A wellness practice session created by a verified master.

    One master can have many practices. Users book practices in Phase 5.
    """

    __tablename__ = "practices"

    # -- Owner --
    master_id: Mapped[UUID] = mapped_column(
        ForeignKey("master_profiles.user_id", ondelete="CASCADE"),
    )

    # -- Core fields --
    practice_type: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(
        String(20),
        default=PracticeStatus.DRAFT.value,
        server_default=PracticeStatus.DRAFT.value,
    )

    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, default=None)

    # -- Scheduling --
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    duration_minutes: Mapped[int] = mapped_column(Integer)
    timezone: Mapped[str] = mapped_column(String(50))

    # -- Capacity --
    max_participants: Mapped[int | None] = mapped_column(Integer, default=None)
    # NOT USED until Phase 5. See header comment.
    current_participants: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
    )

    # -- Zoom (manual for MVP) --
    zoom_link: Mapped[str | None] = mapped_column(String(500), default=None)

    # -- Series support (self-referential FK) --
    parent_practice_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("practices.id", ondelete="SET NULL"),
        default=None,
    )

    def __repr__(self) -> str:
        return (
            f"<Practice id={self.id} type={self.practice_type} "
            f"status={self.status} title={self.title!r}>"
        )
