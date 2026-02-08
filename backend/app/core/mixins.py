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
from uuid import UUID, uuid4

from sqlalchemy import UUID as SA_UUID
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class UUIDMixin:
    """Primary key mixin — UUID v4, auto-generated.

    Every table gets a `id` column of type UUID. We use app-side uuid4()
    instead of server-side gen_random_uuid() so the ID is available
    immediately after object creation (before flush/commit).
    """

    id: Mapped[UUID] = mapped_column(
        SA_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )


class TimestampMixin:
    """Timestamp mixin — created_at and updated_at.

    created_at: set once by the database server on INSERT (server_default).
    updated_at: set by SQLAlchemy ORM on every UPDATE (onupdate).
                NOTE: raw SQL updates bypass this — use ORM for consistency.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
    )
