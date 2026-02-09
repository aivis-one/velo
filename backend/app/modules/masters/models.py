# =============================================================================
# VELO Backend — Master Profile Model
# =============================================================================
#
# One-to-one with User. Created when a user submits a master application.
# Role upgrade (user → master) happens on User.role, not here.
#
# JSONB DATA STRUCTURE:
#   data.account     — status, verification info, rejection history
#   data.availability — accepting bookings flag, availability note
#   data.profile     — bio, methods, experience, certifications
#   data.settings    — auto-confirm, default max participants
#   data.stats       — computed counters (total practices, avg rating)
#
# BALANCE FIELDS:
#   frozen_amount    — funds locked until practice completion (Phase 6)
#   available_amount — funds available for withdrawal (Phase 6)
#   Both are 0 until Phase 6: Payments. Updated by ledger listeners.
#
# RELATIONSHIP STRATEGY:
#   Unidirectional: MasterProfile → User only. User does NOT have a
#   back-reference to MasterProfile. This avoids side-effect imports
#   in main.py. When masters router is added (Phase 2.2), it will
#   import MasterProfile naturally. Bidirectional relationship can
#   be added then if needed.
# =============================================================================

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Numeric, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class MasterProfile(Base):
    """Master profile — extends User with master-specific data.

    Primary key is user_id (not a separate UUID) — enforces one-to-one
    at the database level. No user can have two master profiles.
    """

    __tablename__ = "master_profiles"

    # -- Primary key = Foreign key (one-to-one) --
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # -- JSONB data sandbox --
    # Structured but flexible. Schema validated at application level
    # (Pydantic), not at database level. See JSONB DATA STRUCTURE above.
    data: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        server_default="{}",
    )

    # -- Balance fields (Phase 6: Payments) --
    # Do NOT modify directly — updated by ledger listeners.
    frozen_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        default=Decimal("0"),
        server_default="0",
    )
    available_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        default=Decimal("0"),
        server_default="0",
    )

    # -- Timestamps --
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
    )

    # -- Relationships --
    # Unidirectional: MasterProfile → User. No back_populates on User
    # to avoid requiring MasterProfile import at app startup.
    user: Mapped["User"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        back_populates=None,
    )

    def __repr__(self) -> str:
        status = self.data.get("account", {}).get("status", "unknown")
        return f"<MasterProfile user_id={self.user_id} status={status}>"
