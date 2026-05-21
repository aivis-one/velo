# =============================================================================
# VELO Backend -- Practice Model (Phase 4.1, updated DS-sprint + Calendar)
# =============================================================================
#
# A wellness practice session created by a verified master.
#
# JSONB DATA SANDBOX (Calendar iteration):
#   `data` is a JSONB schema-on-read sandbox, mirroring User.credentials and
#   MasterProfile.data. New, not-yet-stabilized fields live here first; once
#   the DB design settles they migrate to typed columns / external tables.
#
#   data.taxonomy -- catalog facets used by the Calendar filter:
#     {
#       "direction":  "meditation" | "yoga" | "breathwork",  # PracticeDirection
#       "style":      str | null,                            # free-form, e.g. "Кундалини йога"
#       "difficulty": "beginner" | "medium" | "high"         # PracticeDifficulty
#     }
#
#   JSONB SAFETY: inherits JSONBMixin -- mutate ONLY via set_jsonb("data", ...)
#   after a deepcopy. NEVER assign self.data = ... directly (SQLAlchemy will
#   not detect in-place dict mutation -> silent lost update). See core/mixins.py.
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
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.mixins import JSONBMixin, TimestampMixin, UUIDMixin


class PracticeType(enum.StrEnum):
    """Format of a practice session.

    NOTE: this is the *format*, not the content direction. The content
    direction (meditation / yoga / breathwork) lives in data.taxonomy.
    """

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
    DELETED = "deleted"  # Phase 4.2: soft delete for drafts


class PracticeDirection(enum.StrEnum):
    """Content direction of a practice -- the Calendar "Направление" facet.

    Stored inside data.taxonomy.direction (JSONB schema-on-read sandbox).
    Distinct from PracticeType, which is the session *format*.
    """

    MEDITATION = "meditation"
    YOGA = "yoga"
    BREATHWORK = "breathwork"


class PracticeDifficulty(enum.StrEnum):
    """Difficulty level of a practice -- the Calendar "Сложность" facet.

    Stored inside data.taxonomy.difficulty (JSONB schema-on-read sandbox).
    Rendered as filled dots in the UI: beginner ●○○ / medium ●●○ / high ●●●.
    """

    BEGINNER = "beginner"
    MEDIUM = "medium"
    HIGH = "high"


class Practice(JSONBMixin, UUIDMixin, TimestampMixin, Base):
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
    what_to_prepare: Mapped[str | None] = mapped_column(
        Text, default=None,
    )
    contraindications: Mapped[str | None] = mapped_column(
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
    # NEW-7: lowercase "eur" consistent with Payment, Purchase, Withdrawal.
    currency: Mapped[str] = mapped_column(
        String(3),
        default="eur",
        server_default="eur",
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

    # -- JSONB sandbox (Calendar iteration) --
    # Schema-on-read facets (data.taxonomy: direction / style / difficulty).
    # Mutate ONLY via set_jsonb("data", deepcopy(...)). See class docstring.
    data: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        server_default="{}",
    )

    def __repr__(self) -> str:
        return (
            f"<Practice id={self.id} type={self.practice_type} "
            f"status={self.status} title={self.title!r} "
            f"is_free={self.is_free} price_cents={self.price_cents}>"
        )
