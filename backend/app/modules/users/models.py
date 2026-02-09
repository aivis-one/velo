# =============================================================================
# VELO Backend — User Model
# =============================================================================
#
# Central user entity. Every person in the system (student, master, admin)
# is a single User row. Role determines permissions, not separate tables.
#
# AUTH STRATEGY:
#   - telegram_id: indexed column for fast lookup on every login.
#   - credentials: JSONB sandbox for evolving auth data (telegram username,
#     photo_url, future email/password, OAuth tokens, etc.).
#   Rule: search by column, store in JSONB.
#
# BALANCE:
#   balance_user is a cached value computed from user_ledger (Phase 6).
#   Default 0, not touched until Phase 6: Payments.
# =============================================================================

import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.mixins import TimestampMixin, UUIDMixin


class UserRole(str, enum.Enum):
    """User roles in the platform.

    USER:   default role, can browse and book practices.
    MASTER: verified facilitator, can create and host practices.
    ADMIN:  platform operator, can manage users and content.
    """

    USER = "user"
    MASTER = "master"
    ADMIN = "admin"


class User(UUIDMixin, TimestampMixin, Base):
    """Platform user — student, master, or admin.

    One row per person regardless of role. Role upgrades (user → master)
    happen in place, no separate tables.
    """

    __tablename__ = "users"

    # -- Auth --
    # Telegram user ID — unique, indexed, used for login lookup.
    # BigInteger because Telegram IDs can exceed 2^31.
    telegram_id: Mapped[int | None] = mapped_column(
        BigInteger,
        unique=True,
        index=True,
    )

    # JSONB sandbox for auth-related data that doesn't need fast lookup.
    # Current: {telegram_username, telegram_photo_url, raw_init_data}
    # Future: {email, password_hash, google_id, apple_id, ...}
    credentials: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        server_default="{}",
    )

    # -- Role --
    role: Mapped[UserRole] = mapped_column(
        String(20),
        default=UserRole.USER,
        server_default=UserRole.USER.value,
    )

    # -- Profile --
    first_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    timezone: Mapped[str] = mapped_column(
        String(50),
        default="UTC",
        server_default="UTC",
    )
    language: Mapped[str] = mapped_column(
        String(5),
        default="en",
        server_default="en",
    )

    # -- Status --
    is_active: Mapped[bool] = mapped_column(
        default=True,
        server_default="true",
    )

    # -- Balance --
    # Cached value computed from user_ledger (Phase 6: Payments).
    # Do NOT modify directly — use ledger transactions.
    balance_user: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        default=Decimal("0"),
        server_default="0",
    )

    # -- Timestamps (extra) --
    # last_login_at is NOT in TimestampMixin because it's domain-specific.
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    # -- Relationships --
    # Async SQLAlchemy: default lazy loading will raise MissingGreenlet
    # if accessed without explicit loading. This is intentional —
    # master_profile should be loaded explicitly in masters module
    # queries, not on every User access.
    master_profile: Mapped["MasterProfile | None"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        back_populates="user",
        uselist=False,
    )

    def __repr__(self) -> str:
        return (
            f"<User id={self.id} " f"tg={self.telegram_id} " f"role={self.role.value}>"
        )
