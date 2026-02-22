# =============================================================================
# VELO Backend -- Notification Channel Formatters (Phase 7.2)
# =============================================================================
#
# Each delivery channel has a formatter that knows how to:
#   1. Convert action_data into a channel-specific deep link
#   2. Build channel_options (buttons, parse mode, etc.)
#   3. Send the notification (or stub-log it)
#
# ARCHITECTURE:
#   ChannelFormatter (Protocol) defines the interface.
#   StubFormatter logs instead of sending -- used until real channels
#   are implemented (Telegram in Phase 7.3).
#
# FORMATTER REGISTRY:
#   get_formatter(channel) returns the appropriate formatter instance.
#   Unknown channels get StubFormatter (safe fallback + logged warning).
#
# ADDING A NEW CHANNEL (Phase 7.3+):
#   1. Create TelegramFormatter implementing ChannelFormatter
#   2. Register in _FORMATTERS dict
#   3. Done -- processor picks it up automatically
# =============================================================================

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import structlog

logger = structlog.get_logger()


@dataclass
class DeliveryResult:
    """Result of a send attempt."""

    success: bool
    error_message: str | None = None


class ChannelFormatter(Protocol):
    """Interface for channel-specific notification delivery."""

    def format_deep_link(self, action_data: dict | None) -> str | None:
        """Convert action_data to a channel-specific URL/link."""
        ...

    async def send(
        self,
        *,
        title: str,
        body: str,
        user_telegram_id: int | None,
        deep_link: str | None,
        channel_options: dict | None,
    ) -> DeliveryResult:
        """Send the notification via this channel.

        Args:
            title: Notification title.
            body: Notification body text.
            user_telegram_id: Recipient's Telegram ID (if available).
            deep_link: Channel-specific deep link (from format_deep_link).
            channel_options: Per-delivery JSONB options.

        Returns:
            DeliveryResult with success flag and optional error.
        """
        ...


class StubFormatter:
    """Stub formatter that logs instead of sending.

    Used for all channels until real implementations are added.
    Phase 7.3 will replace Telegram with TelegramFormatter.
    """

    def format_deep_link(self, action_data: dict | None) -> str | None:
        """Format deep link as a readable string for logging."""
        if not action_data:
            return None
        action = action_data.get("action", "unknown")
        params = action_data.get("params", {})
        if params:
            param_str = "_".join(str(v) for v in params.values())
            return f"stub://{action}/{param_str}"
        return f"stub://{action}"

    async def send(
        self,
        *,
        title: str,
        body: str,
        user_telegram_id: int | None,
        deep_link: str | None,
        channel_options: dict | None,
    ) -> DeliveryResult:
        """Log the notification instead of sending it."""
        logger.info(
            "notification_delivered_stub",
            title=title,
            body=body[:100],
            telegram_id=user_telegram_id,
            deep_link=deep_link,
            channel_options=channel_options,
        )
        return DeliveryResult(success=True)


# ---------------------------------------------------------------------------
# Formatter registry
# ---------------------------------------------------------------------------

_stub = StubFormatter()

_FORMATTERS: dict[str, ChannelFormatter] = {
    # Phase 7.3: "telegram": TelegramFormatter(bot_token=...)
}


def get_formatter(channel: str) -> ChannelFormatter:
    """Get the formatter for a delivery channel.

    Falls back to StubFormatter for unregistered channels.
    """
    formatter = _FORMATTERS.get(channel)
    if formatter is not None:
        return formatter

    logger.debug(
        "formatter_stub_fallback",
        channel=channel,
    )
    return _stub
