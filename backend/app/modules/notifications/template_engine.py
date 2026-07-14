# =============================================================================
# VELO Backend -- Notification Template Engine (Phase 7.3)
# =============================================================================
#
# Multilingual notification templates loaded from YAML files.
#
# ARCHITECTURE:
#   - Templates stored in notifications/templates/{lang}.yaml
#   - Loaded into memory cache at app startup (lifespan)
#   - SafeDict for safe format_map (missing keys -> "{key}" literal)
#   - Language fallback: requested lang -> "en"
#   - Admin reload endpoint: POST /api/v1/admin/templates/reload
#
# YAML FORMAT:
#   booking_confirmed:
#     title: "Booking confirmed"
#     body: "Your booking for <b>{practice_title}</b> is confirmed."
#
# SUPPORTED LANGUAGES: en, de, es, ru
#
# RENDER:
#   render(notification_type, lang, variables) -> (title, body) | None
#   Variables come from Notification.action_data JSONB.
# =============================================================================

import html
from pathlib import Path
from typing import Any

import structlog
import yaml

logger = structlog.get_logger()

# Directory containing YAML template files.
_TEMPLATES_DIR = Path(__file__).parent / "templates"

# Supported languages (must have corresponding YAML files).
SUPPORTED_LANGUAGES = frozenset({"en", "de", "es", "ru"})

# Default fallback language.
DEFAULT_LANGUAGE = "en"

# In-memory cache: (notification_type, lang) -> {"title": str, "body": str}
_cache: dict[tuple[str, str], dict[str, str]] = {}


# ===================================================================
# SafeDict -- missing keys return "{key}" instead of raising KeyError
# ===================================================================


class SafeDict(dict):
    """Dict subclass for safe str.format_map() calls.

    Missing keys produce the literal placeholder (e.g. "{name}")
    instead of raising KeyError. Prevents crashes when action_data
    is incomplete or template has extra placeholders.
    """

    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def _escape_string_values(variables: dict[str, Any]) -> dict[str, Any]:
    """HTML-escape every string value in `variables` before it's interpolated
    into a template. Non-string values (counts, etc.) pass through unchanged --
    only user-controlled text (practice titles, display names, ...) needs
    escaping. The template markup itself (the `<b>`/`<i>` tags surrounding
    `{placeholder}` in the YAML) is untouched -- this only escapes the
    SUBSTITUTED values, never the template string.

    Without this, a practice title or display name containing `&`/`<`/`>`
    either breaks Telegram's HTML parser (send_message rejects the whole
    message) or, worse, renders as live markup (e.g. an injected `<a href>`
    link) inside a notification sent to someone else.
    """
    return {
        key: html.escape(value) if isinstance(value, str) else value
        for key, value in variables.items()
    }


# ===================================================================
# Loading
# ===================================================================


def load_templates() -> int:
    """Load all YAML template files into the in-memory cache.

    Clears existing cache before loading. Safe to call multiple times
    (used by admin reload endpoint).

    Returns:
        Total number of (type, lang) entries loaded.
    """
    global _cache
    new_cache: dict[tuple[str, str], dict[str, str]] = {}

    for lang in SUPPORTED_LANGUAGES:
        filepath = _TEMPLATES_DIR / f"{lang}.yaml"
        if not filepath.exists():
            logger.warning(
                "template_file_missing",
                lang=lang,
                path=str(filepath),
            )
            continue

        try:
            with open(filepath, encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception:
            logger.exception(
                "template_file_load_error",
                lang=lang,
                path=str(filepath),
            )
            continue

        if not isinstance(data, dict):
            logger.warning(
                "template_file_invalid_format",
                lang=lang,
                path=str(filepath),
            )
            continue

        for key, template in data.items():
            if not isinstance(template, dict):
                logger.warning(
                    "template_entry_invalid",
                    lang=lang,
                    key=key,
                )
                continue

            title = template.get("title", "")
            body = template.get("body", "")

            if not title or not body:
                logger.warning(
                    "template_entry_incomplete",
                    lang=lang,
                    key=key,
                )
                continue

            new_cache[(key, lang)] = {
                "title": str(title),
                "body": str(body),
            }

    _cache = new_cache

    logger.info(
        "templates_loaded",
        total=len(_cache),
        languages=sorted(SUPPORTED_LANGUAGES),
    )

    return len(_cache)


def reload_templates() -> int:
    """Reload templates from disk. Alias for load_templates().

    Exposed separately for semantic clarity at call sites.
    """
    return load_templates()


# ===================================================================
# Rendering
# ===================================================================


def render(
    notification_type: str,
    lang: str,
    variables: dict[str, Any] | None = None,
) -> tuple[str, str] | None:
    """Render a notification template with variable substitution.

    Looks up (notification_type, lang) in cache, falls back to
    (notification_type, "en") if not found.

    Args:
        notification_type: Template key (matches NotificationType values).
        lang: User language code (e.g. "en", "de", "ru", "es").
        variables: Dict of placeholder values from action_data.

    Returns:
        (title, body) tuple with placeholders replaced, or None
        if template not found in any language.
    """
    if not _cache:
        logger.warning("templates_not_loaded")
        return None

    # Normalize language to supported set.
    normalized_lang = normalize_language(lang)

    # Lookup: requested language -> fallback to "en".
    template = _cache.get((notification_type, normalized_lang))
    if template is None and normalized_lang != DEFAULT_LANGUAGE:
        template = _cache.get((notification_type, DEFAULT_LANGUAGE))

    if template is None:
        logger.warning(
            "template_not_found",
            notification_type=notification_type,
            lang=normalized_lang,
        )
        return None

    safe_vars = SafeDict(_escape_string_values(variables or {}))

    try:
        title = template["title"].format_map(safe_vars)
        body = template["body"].format_map(safe_vars)
    except Exception:
        logger.exception(
            "template_render_error",
            notification_type=notification_type,
            lang=normalized_lang,
        )
        return None

    return title, body


# ===================================================================
# Helpers
# ===================================================================


def normalize_language(lang: str | None) -> str:
    """Normalize language code to a supported value.

    Handles cases like "en-US" -> "en", "DE" -> "de", None -> "en".
    """
    if not lang:
        return DEFAULT_LANGUAGE

    # Take first 2 chars (handles "en-US", "pt-BR", etc.).
    short = lang[:2].lower()

    if short in SUPPORTED_LANGUAGES:
        return short

    return DEFAULT_LANGUAGE


def get_supported_languages() -> list[str]:
    """Return sorted list of supported language codes."""
    return sorted(SUPPORTED_LANGUAGES)


def get_cache_stats() -> dict[str, int]:
    """Return cache statistics for admin/debug."""
    langs: dict[str, int] = {}
    for (_, lang) in _cache:
        langs[lang] = langs.get(lang, 0) + 1
    return {
        "total_entries": len(_cache),
        "per_language": langs,
    }
