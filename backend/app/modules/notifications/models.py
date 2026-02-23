# =============================================================================
# VELO Backend -- Notification Models (Phase 7.1, updated Phase 7.4)
# =============================================================================
#
# Two-level architecture:
#   Notification  -- WHAT to send, WHERE to route (channel-agnostic).
#   NotificationDelivery -- WHO receives it, via WHICH channel, status.
#
# NOTIFICATION:
#   Stores the semantic payload: type, title, body, target audience,
#   deep-link intent (action_data JSONB), priority, scheduling, expiry.
#   One notification can produce N deliveries (e.g. "practice cancelled"
#   -> one delivery per booked user).
#
# NOTIFICATION DELIVERY:
#   Per-user, per-channel delivery attempt. Tracks status, retry count,
#   error messages, and channel-specific options (JSONB).
#   channel_options format depends on channel:
#     telegram:  {parse_mode, disable_preview, silent, auto_delete, buttons}
#     web_push:  {icon, action_url, ttl}
#     in_app:    {action_url, dismissable}
#
# TARGET ROUTING:
#   target_type + target_value define the audience:
#     user:<uuid>      -- single user (reminders, booking confirmations)
#     practice:<uuid>  -- all participants (cancellation, schedule change)
#     role:master      -- all masters (system announcements)
#     all              -- broadcast
#   Processor (Phase 7.2) resolves targets into individual deliveries.
#
# ACTION DATA (deep linking):
#   action_data JSONB stores channel-agnostic navigation intent:
#     {"action": "open_practice", "params": {"practice_id": "uuid"}}
#   Channel formatters (Phase 7.2-7.3) convert to platform-specific
#   deep links at delivery time:
#     Telegram -> "https://t.me/velobot?startapp=practice_uuid"
#     Web push -> "/practices/uuid"
#
# UUID PRIMARY KEYS:
#   UUID for consistency with the rest of the project.
#
# SESSION RULES:
#   No session.commit() in service (P-01). Service layer uses flush.
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
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.mixins import TimestampMixin, UUIDMixin


# ===================================================================
# Enums
# ===================================================================


class NotificationType(enum.StrEnum):
    """Semantic type of notification -- what happened."""

    # Reminders (Phase 7.4).
    REMINDER_24H = "reminder_24h"
    REMINDER_1H = "reminder_1h"
    REMINDER_10MIN = "reminder_10min"

    # Master reminders (Phase 7.4).
    MASTER_REMINDER_24H = "master_reminder_24h"
    MASTER_REMINDER_1H = "master_reminder_1h"
    MASTER_REMINDER_10MIN = "master_reminder_10min"

    # Booking lifecycle.
    BOOKING_CONFIRMED = "booking_confirmed"
    BOOKING_CANCELLED = "booking_cancelled"

    # Practice lifecycle.
    PRACTICE_CANCELLED = "practice_cancelled"
    PRACTICE_UPDATED = "practice_updated"

    # Waitlist (Phase 5.3 stubs -> real notifications).
    WAITLIST_SPOT_AVAILABLE = "waitlist_spot_available"
    WAITLIST_EXPIRED = "waitlist_expired"

    # Master verification.
    MASTER_VERIFIED = "master_verified"
    MASTER_REJECTED = "master_rejected"

    # Payments.
    TOPUP_CONFIRMED = "topup_confirmed"
    WITHDRAWAL_APPROVED = "withdrawal_approved"
    WITHDRAWAL_REJECTED = "withdrawal_rejected"

    # Feedback nudge (Phase 8).
    LEAVE_REVIEW = "leave_review"
    LEAVE_FEEDBACK = "leave_feedback"

    # System.
    SYSTEM_ANNOUNCEMENT = "system_announcement"


class NotificationStatus(enum.StrEnum):
    """Lifecycle status of a Notification record."""

    PENDING = "pending"
    PROCESSING = "processing"
    SENT = "sent"
    FAILED = "failed"
    EXPIRED = "expired"


class DeliveryStatus(enum.StrEnum):
    """Delivery attempt status per user per channel."""

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class DeliveryChannel(enum.StrEnum):
    """Supported delivery channels."""

    TELEGRAM = "telegram"
    WEB_PUSH = "web_push"
    IN_APP = "in_app"
    EMAIL = "email"


class TargetType(enum.StrEnum):
    """Audience targeting strategy."""

    USER = "user"
    PRACTICE = "practice"
    ROLE = "role"
    ALL = "all"


# ===================================================================
# Notification
# ===================================================================


class Notification(UUIDMixin, TimestampMixin, Base):
    """A channel-agnostic notification record.

    Stores the semantic payload (what happened, who should know,
    where to navigate). The processor (Phase 7.2) resolves the
    target into individual NotificationDelivery rows.
    """

    __tablename__ = "notifications"

    # -- Semantic type --
    type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True,
    )

    # -- Content (channel-agnostic) --
    title: Mapped[str] = mapped_column(
        String(200), nullable=False,
    )
    body: Mapped[str] = mapped_column(
        Text, nullable=False,
    )

    # -- Target audience --
    # Processor resolves (target_type, target_value) into deliveries.
    target_type: Mapped[str] = mapped_column(
        String(20), nullable=False,
    )
    target_value: Mapped[str] = mapped_column(
        String(200), nullable=False,
    )

    # -- Deep link intent (channel-agnostic) --
    # {"action": "open_practice", "params": {"practice_id": "uuid"}}
    # Channel formatters convert to platform-specific URLs at send time.
    action_data: Mapped[dict | None] = mapped_column(
        JSONB, default=None, nullable=True,
    )

    # -- Scheduling & priority --
    priority: Mapped[int] = mapped_column(
        Integer, default=5, server_default="5",
    )
    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
    )
    expiry_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True,
    )

    # -- Status --
    status: Mapped[str] = mapped_column(
        String(20),
        default=NotificationStatus.PENDING.value,
        server_default=NotificationStatus.PENDING.value,
        index=True,
    )

    def __repr__(self) -> str:
        return (
            f"<Notification id={self.id} type={self.type} "
            f"target={self.target_type}:{self.target_value} "
            f"status={self.status}>"
        )


# ===================================================================
# NotificationDelivery
# ===================================================================


class NotificationDelivery(UUIDMixin, TimestampMixin, Base):
    """Per-user, per-channel delivery attempt.

    Created by the notification processor when it resolves a
    Notification's target into individual recipients. Tracks
    delivery status, retry count, and channel-specific options.

    channel_options JSONB format varies by channel:
      telegram:  {parse_mode, disable_preview, silent, auto_delete, buttons}
      web_push:  {icon, action_url, ttl}
      in_app:    {action_url, dismissable}
    """

    __tablename__ = "notification_deliveries"

    # -- Parent notification --
    notification_id: Mapped[UUID] = mapped_column(
        ForeignKey("notifications.id", ondelete="CASCADE"),
        index=True,
    )

    # -- Recipient --
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )

    # -- Channel --
    channel: Mapped[str] = mapped_column(
        String(20), nullable=False,
    )

    # -- Channel-specific options --
    channel_options: Mapped[dict | None] = mapped_column(
        JSONB, default=None, nullable=True,
    )

    # -- Delivery status --
    status: Mapped[str] = mapped_column(
        String(20),
        default=DeliveryStatus.PENDING.value,
        server_default=DeliveryStatus.PENDING.value,
    )
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True,
    )
    attempts: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0",
    )
    error_message: Mapped[str | None] = mapped_column(
        Text, default=None, nullable=True,
    )

    def __repr__(self) -> str:
        return (
            f"<NotificationDelivery id={self.id} "
            f"notification={self.notification_id} "
            f"user={self.user_id} channel={self.channel} "
            f"status={self.status} attempts={self.attempts}>"
        )
