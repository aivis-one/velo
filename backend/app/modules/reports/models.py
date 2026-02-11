# =============================================================================
# VELO Backend -- Report Model (Phase 3.3)
# =============================================================================
#
# User-submitted reports (complaints) about other users, masters, or
# practices. Admins can resolve or dismiss reports.
#
# POLYMORPHIC TARGET:
#   target_type + target_id form a polymorphic reference. No FK constraint
#   because target can be in different tables (users, master_profiles,
#   practices). Validation happens at application level in service.py.
#
# DUPLICATE PREVENTION:
#   UniqueConstraint on (reporter_id, target_type, target_id) -- one
#   report per user per target. If user tries to report again, they
#   get their existing report back with a prompt to edit it.
#
# STATE MACHINE:
#   pending -> resolved  (admin resolves)
#   pending -> dismissed (admin dismisses)
#   No other transitions allowed. Uses with_for_update() (P-12).
#
# SESSION RULES:
#   No session.commit() in service (P-01). Router calls flush + refresh.
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


class ReportStatus(enum.StrEnum):
    """Report lifecycle statuses."""

    PENDING = "pending"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class ReportTargetType(enum.StrEnum):
    """Allowed target types for reports."""

    USER = "user"
    MASTER = "master"
    PRACTICE = "practice"


class Report(UUIDMixin, TimestampMixin, Base):
    """User-submitted complaint about a user, master, or practice.

    One report per (reporter, target_type, target_id) combination.
    Admins resolve or dismiss pending reports.
    """

    __tablename__ = "reports"

    # -- Who reported --
    reporter_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
    )

    # -- What was reported (polymorphic) --
    # No FK -- target can be in users, master_profiles, or practices.
    target_type: Mapped[str] = mapped_column(String(20))
    target_id: Mapped[UUID] = mapped_column()

    # -- Report content --
    reason: Mapped[str] = mapped_column(Text)

    # -- Status --
    status: Mapped[str] = mapped_column(
        String(20),
        default=ReportStatus.PENDING.value,
        server_default=ReportStatus.PENDING.value,
    )

    # -- Resolution (filled by admin) --
    resolved_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        default=None,
    )
    resolution_note: Mapped[str | None] = mapped_column(Text, default=None)
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=None,
    )

    __table_args__ = (
        UniqueConstraint(
            "reporter_id",
            "target_type",
            "target_id",
            name="uq_report_reporter_target",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Report id={self.id} target={self.target_type}:{self.target_id} "
            f"status={self.status}>"
        )
