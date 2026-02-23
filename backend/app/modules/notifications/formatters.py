# =============================================================================
# VELO Backend -- Notification Channel Formatters (Phase 7.2, updated 7.3)
# =============================================================================
#
# Each delivery channel has a formatter that knows how to:
#   1. Convert action_data into a channel-specific deep link
#   2. Send the notification (or stub-log it)
#
# ARCHITECTURE:
#   ChannelFormatter (Protocol) defines the interface.
#   StubFormatter logs instead of sending -- fallback for unconfigured channels.
#   TelegramFormatter (Phase 7.3) sends via aiogram Bot.send_message().
#
# FORMATTER REGISTRY:
#   get_formatter(channel) returns the appropriate formatter instance.
#   Telegram formatter is lazily initialized on first call.
#   Unknown channels get StubFormatter (safe fallback + logged warning).
#
# TELEGRAM ERROR HANDLING:
#   "bot was blocked by user" / "chat not found" -> immediate failure
#   (no retries -- these are permanent). All other errors -> DeliveryResult
#   with success=False, processor will retry up to max_attempts.
#
# ADDING A NEW CHANNEL:
#   1. Create formatter class implementing ChannelFormatter protocol
#   2. Register in _FORMATTERS dict (or lazy-init in get_formatter)
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
    # Permanent failure -- processor should NOT retry (e.g. user blocked bot).
    permanent: bool = False


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
            title: Notification title (already rendered from template).
            body: Notification body text (already rendered, HTML).
            user_telegram_id: Recipient's Telegram ID (if available).
            deep_link: Channel-specific deep link (from format_deep_link).
            channel_options: Per-delivery JSONB options.

        Returns:
            DeliveryResult with success flag and optional error.
        """
        ...


class StubFormatter:
    """Stub formatter that logs instead of sending.

    Used for all channels until real implementations are added,
    and as fallback when Telegram bot token is not configured.
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


# ===================================================================
# TelegramFormatter (Phase 7.3)
# ===================================================================

# Telegram API error substrings that indicate permanent failure.
# No point retrying these -- user must unblock or start the bot.
_PERMANENT_ERRORS = frozenset({
    "bot was blocked by the user",
    "user is deactivated",
    "chat not found",
    "bot can't initiate conversation",
    "have no rights to send a message",
})


class TelegramFormatter:
    """Send notifications via Telegram Bot API (aiogram 3.x).

    Uses Bot.send_message() only -- no Dispatcher, no polling,
    no event loop conflict with uvicorn (see LLM-Code-Review-Guide
    Phase 7 warning #3).
    """

    def __init__(self, bot: "aiogram.Bot", bot_url: str) -> None:  # noqa: F821
        """Initialize with aiogram Bot instance and bot URL.

        Args:
            bot: Aiogram Bot instance (already configured with token).
            bot_url: Base URL for deep links (e.g. "https://t.me/velo_testbot").
        """
        self._bot = bot
        self._bot_url = bot_url.rstrip("/")

    def format_deep_link(self, action_data: dict | None) -> str | None:
        """Convert action_data to a Telegram WebApp deep link.

        Format: https://t.me/velo_testbot?startapp={action}__{param1}_{param2}

        Args:
            action_data: {"action": "open_practice", "params": {"practice_id": "uuid"}}

        Returns:
            Deep link URL or None if no action_data.
        """
        if not action_data:
            return None

        action = action_data.get("action")
        if not action:
            return None

        params = action_data.get("params", {})
        if params:
            param_str = "_".join(str(v) for v in params.values())
            return f"{self._bot_url}?startapp={action}__{param_str}"

        return f"{self._bot_url}?startapp={action}"

    async def send(
        self,
        *,
        title: str,
        body: str,
        user_telegram_id: int | None,
        deep_link: str | None,
        channel_options: dict | None,
    ) -> DeliveryResult:
        """Send notification via Telegram Bot API.

        Builds HTML message from title + body, optionally adds an
        inline keyboard button with the deep link.

        Args:
            title: Already-rendered notification title.
            body: Already-rendered notification body (HTML).
            user_telegram_id: Recipient Telegram chat ID.
            deep_link: WebApp deep link URL (for inline button).
            channel_options: Per-delivery JSONB options.

        Returns:
            DeliveryResult with success/error info.
        """
        if not user_telegram_id:
            return DeliveryResult(
                success=False,
                error_message="No telegram_id for user",
                permanent=True,
            )

        # Lazy import to avoid import-time dependency on aiogram.
        from aiogram.enums import ParseMode
        from aiogram.exceptions import TelegramAPIError
        from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

        # Build message text.
        text = f"<b>{title}</b>\n\n{body}"

        # Build inline keyboard if deep link available.
        keyboard = None
        if deep_link:
            # Determine button label from channel_options or default.
            button_text = "Open"
            if channel_options and "button_text" in channel_options:
                button_text = channel_options["button_text"]

            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=button_text, url=deep_link)]
                ]
            )

        # Apply channel_options overrides.
        disable_preview = True
        silent = False
        if channel_options:
            disable_preview = channel_options.get("disable_preview", True)
            silent = channel_options.get("silent", False)

        try:
            await self._bot.send_message(
                chat_id=user_telegram_id,
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
                disable_web_page_preview=disable_preview,
                disable_notification=silent,
            )

            logger.info(
                "notification_delivered_telegram",
                telegram_id=user_telegram_id,
                title=title,
            )

            return DeliveryResult(success=True)

        except TelegramAPIError as exc:
            error_msg = str(exc).lower()

            # Check for permanent failures -- no retry.
            for perm_error in _PERMANENT_ERRORS:
                if perm_error in error_msg:
                    logger.warning(
                        "notification_delivery_permanent_failure",
                        telegram_id=user_telegram_id,
                        error=str(exc),
                    )
                    return DeliveryResult(
                        success=False,
                        error_message=str(exc),
                        permanent=True,
                    )

            # Transient error -- processor will retry.
            logger.warning(
                "notification_delivery_telegram_error",
                telegram_id=user_telegram_id,
                error=str(exc),
            )
            return DeliveryResult(
                success=False,
                error_message=str(exc),
            )

        except Exception as exc:
            logger.exception(
                "notification_delivery_unexpected_error",
                telegram_id=user_telegram_id,
            )
            return DeliveryResult(
                success=False,
                error_message=f"Unexpected: {exc}",
            )


# ---------------------------------------------------------------------------
# Formatter registry (lazy initialization)
# ---------------------------------------------------------------------------

_stub = StubFormatter()
_telegram_formatter: TelegramFormatter | None = None
_telegram_init_attempted: bool = False


def _init_telegram_formatter() -> TelegramFormatter | None:
    """Lazily initialize TelegramFormatter from settings.

    Creates an aiogram Bot instance if telegram_bot_token is a real
    token (not the dev placeholder). Called once on first
    get_formatter("telegram") call.

    Returns:
        TelegramFormatter or None if token is not configured.
    """
    global _telegram_formatter, _telegram_init_attempted
    _telegram_init_attempted = True

    from app.core.config import settings

    token = settings.telegram_bot_token
    bot_url = settings.telegram_bot_url

    # Skip if using dev placeholder token.
    if not token or "fake" in token.lower() or "dev" in token.lower():
        logger.info(
            "telegram_formatter_skipped",
            reason="Dev/fake bot token -- using StubFormatter",
        )
        return None

    if not bot_url:
        logger.warning(
            "telegram_formatter_skipped",
            reason="telegram_bot_url not configured",
        )
        return None

    try:
        from aiogram import Bot

        bot = Bot(token=token)
        _telegram_formatter = TelegramFormatter(bot=bot, bot_url=bot_url)

        logger.info(
            "telegram_formatter_initialized",
            bot_url=bot_url,
        )

        return _telegram_formatter

    except Exception:
        logger.exception("telegram_formatter_init_error")
        return None


def get_formatter(channel: str) -> ChannelFormatter:
    """Get the formatter for a delivery channel.

    Telegram formatter is lazily initialized on first call.
    Falls back to StubFormatter for unregistered or failed channels.
    """
    global _telegram_formatter, _telegram_init_attempted

    if channel == "telegram":
        if _telegram_formatter is not None:
            return _telegram_formatter

        if not _telegram_init_attempted:
            formatter = _init_telegram_formatter()
            if formatter is not None:
                return formatter

        # Fall through to stub.
        logger.debug("formatter_stub_fallback", channel=channel)
        return _stub

    # All other channels: stub for now.
    logger.debug("formatter_stub_fallback", channel=channel)
    return _stub
