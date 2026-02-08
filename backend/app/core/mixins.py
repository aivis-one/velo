# =============================================================================
# VELO Backend — ORM Mixins
# =============================================================================
#
# Reusable column sets for SQLAlchemy models. Every model in VELO inherits
# from these instead of duplicating id/created_at/updated_at definitions.
#
# USAGE:
#   class User(UUIDMixin, TimestampMixin, Base):
#       __tablename__ = "users"
#       ...
#
# WHY MIXINS (not a custom Base)?
#   Alembic reads Base.metadata for autogenerate. If we subclass Base,
#   the mixin tables appear in metadata and Alembic tries to create them.
#   Mixins with `MappedAsDataclass=False` and `__abstract__ = True` avoid this.
# =============================================================================

from datetime import datetime
from uuid import uuid4

from sqlalchemy import UUID, func
from sqlalchemy.orm import Mapped, mapped_column


class UUIDMixin:
    """Primary key mixin — UUID v4, auto-generated.

    Every table gets a `id` column of type UUID. We use app-side uuid4()
    instead of server-side gen_random_uuid() so the ID is available
    immediately after object creation (before flush/commit).
    """

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )


class TimestampMixin:
    """Timestamp mixin — created_at and updated_at.

    created_at: set once by the database server on INSERT.
    updated_at: set by the database server on every UPDATE.

    Using server_default/server_onupdate ensures consistency even if
    the app clock drifts or the record is updated via raw SQL.
    """

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        onupdate=func.now(),
    )
