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
# BALANCE (Phase 6.1, TD-033):
#   balance_cents is a cached value in EUR cents computed from user_ledger.
#   Updated by ledger listeners (Phase 6.2). Do NOT modify directly.
# =============================================================================

import enum
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.mixins import TimestampMixin, UUIDMixin


class UserRole(enum.StrEnum):
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

    # -- Balance (Phase 6.1, TD-033) --
    # Cached value in EUR cents computed from user_ledger.
    # 1500 = €15.00. Do NOT modify directly — use ledger transactions.
    balance_cents: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
    )

    # -- Timestamps (extra) --
    # last_login_at is NOT in TimestampMixin because it's domain-specific.
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    def __repr__(self) -> str:
        return (
            f"<User id={self.id} "
            f"tg={self.telegram_id} "
            f"role={self.role.value}>"
        )

    # -- Balance guard (Phase 6.2) --
    # Warns if balance_cents is set directly instead of via
    # record_user_ledger(). Does NOT block — just logs a warning.
    _GUARDED_FIELDS = frozenset({"balance_cents"})

    def __setattr__(self, name: str, value: object) -> None:
        if name in self._GUARDED_FIELDS:
            import structlog
            structlog.get_logger().warning(
                "direct_balance_write",
                field=name,
                hint="Use record_user_ledger() instead",
            )
        super().__setattr__(name, value)
