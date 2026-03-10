# =============================================================================
# VELO Backend -- Application Configuration (updated Phase 8.1, WARNING-5)
# =============================================================================
#
# HOW IT WORKS:
#   1. pydantic-settings reads your .env file
#   2. Each field here maps to an environment variable (case-insensitive)
#   3. Pydantic validates types: if DATABASE_URL is missing or malformed,
#      the app crashes at startup with a clear error -- not at runtime
#      when a user triggers a database query.
#
# EXAMPLE:
#   .env contains:       DATABASE_URL=postgresql+asyncpg://...
#   Python code uses:    settings.database_url  (typed as str, validated)
#
# WHY NOT just os.getenv()?
#   os.getenv("DATABSE_URL")  <- typo, returns None, crashes later
#   settings.databse_url      <- typo, IDE catches it immediately
#
# SECURITY (TD-001, TD-006):
#   In production (APP_ENV != development), SECRET_KEY and DATABASE_URL
#   have no defaults -- the app refuses to start without a proper .env.
#   In development, safe defaults are provided for convenience.
#
# WARNING-5: STRIPE_STUB is disallowed in production.
#   If STRIPE_SECRET_KEY="TEST", webhook signature verification is skipped.
#   The validator below raises at startup if this happens in production.
# =============================================================================

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, loaded from environment variables.

    Each field corresponds to an env var. Pydantic handles:
    - Type conversion (str -> int, str -> bool)
    - Validation (missing required vars -> clear error at startup)
    - Defaults (optional vars get fallback values)
    """

    # -- Application --
    app_env: str = "development"

    # -- Database --
    # Full async connection string for SQLAlchemy.
    # Port 5433: Docker dev setup (5432 reserved for native postgres).
    # Default provided for development only. (TD-006)
    database_url: str = ""

    # Docker Compose uses these to create the database on first run.
    # Must match the user/pass/db in DATABASE_URL above.
    postgres_db: str = "velo"
    postgres_user: str = "velo"
    postgres_password: str = "velo"

    # -- Redis --
    redis_url: str = "redis://localhost:6379/0"

    # -- CORS --
    # Comma-separated list of allowed origins.
    # "*" for development, specific domains for production.
    cors_origins: str = "*"

    # -- Security --
    # No default in production -- app won't start without it. (TD-001)
    secret_key: str = ""

    # -- Telegram --
    # Bot token from BotFather. Required for initData validation.
    # Dev default is a fake token -- HMAC won't match real Telegram data,
    # but tests mock validation anyway. (P-4)
    telegram_bot_token: str = ""
    # Bot URL for deep link buttons in notifications (Phase 7.3).
    # Example: "https://t.me/velo_testbot"
    telegram_bot_url: str = ""

    # -- Sessions --
    # How long a session token lives in Redis (days).
    session_ttl_days: int = 30

    # -- Logging --
    # CQ-06: default INFO (not DEBUG) -- DEBUG is too noisy for production
    # and even dev. Override with LOG_LEVEL=DEBUG in .env if needed.
    log_level: str = "INFO"

    # -- Practices (Phase 4.2) --
    practice_min_duration_minutes: int = 5
    practice_max_duration_minutes: int = 480

    # -- Stripe (Phase 6.3) --
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_success_url: str = ""
    stripe_cancel_url: str = ""

    # -- Topup limits (Phase 6.3) --
    # All amounts in EUR cents.
    min_topup_cents: int = 100      # EUR 1.00
    max_topup_cents: int = 50000    # EUR 500.00
    default_currency: str = "eur"

    # -- Commission (Phase 6.4) --
    # Platform commission deducted from master earnings on practice completion.
    # Integer percent: 15 = 15%.
    commission_percent: int = 15

    # -- Cancellation (Phase 6.5) --
    # Hours before practice.scheduled_at when free cancellation is allowed.
    # Cancel > N hours before -> 100% refund.
    # Cancel <= N hours before -> 0% refund (early finalize, master keeps money).
    cancellation_deadline_hours: int = 24

    # -- Withdrawals (Phase 6.6) --
    # Minimum withdrawal amount in EUR cents. 5000 = EUR 50.00.
    min_withdrawal_cents: int = 5000
    # Fixed platform fee deducted from withdrawal amount. 200 = EUR 2.00.
    withdrawal_fee_cents: int = 200

    # -- Promos (Phase 6.7) --
    # Allowed discount percentages for both company and master promos.
    # Validated in service layer when creating a promo.
    promo_allowed_discounts: list[int] = [5, 25, 50, 75, 100]

    # -- Notifications (Phase 7.2) --
    # Processor polling interval in seconds (resets on work found).
    notification_poll_interval_seconds: int = 5
    # Max backoff when queue is empty (exponential up to this).
    notification_max_backoff_seconds: int = 60
    # Max delivery attempts before marking as failed.
    notification_max_delivery_attempts: int = 3

    # -- Diary (Phase 8) --
    # Hours before practice.scheduled_at when check-in window opens.
    checkin_window_hours: int = 3
    # Hours after practice completion when feedback window closes.
    feedback_window_hours: int = 72
    # Max length of comment in check-ins and feedbacks.
    # SUGGESTION-12.1: sourced here and referenced in diary/schemas.py
    # via settings.diary_comment_max_length -- change once, applies everywhere.
    diary_comment_max_length: int = 1000

    @model_validator(mode="after")
    def _apply_env_defaults_and_validate(self) -> "Settings":
        """Apply safe defaults for development, enforce secrets in production.

        Development: provides working defaults so `make run` works without .env.
        Production: crashes at startup if critical secrets are missing.
        """
        is_dev = self.app_env == "development"

        # DATABASE_URL: default only in dev (TD-006)
        if not self.database_url:
            if is_dev:
                self.database_url = (
                    "postgresql+asyncpg://velo:velo@localhost:5433/velo"
                )
            else:
                raise ValueError(
                    "DATABASE_URL is required in production. "
                    "Set it in .env file."
                )

        # SECRET_KEY: default only in dev (TD-001)
        if not self.secret_key:
            if is_dev:
                self.secret_key = (
                    "dev-only-insecure-key-do-not-use-in-production"
                )
            else:
                raise ValueError(
                    "SECRET_KEY is required in production. "
                    'Generate with: python -c "import secrets; '
                    'print(secrets.token_urlsafe(64))"'
                )

        # TELEGRAM_BOT_TOKEN: required in production.
        if not self.telegram_bot_token:
            if is_dev:
                self.telegram_bot_token = (
                    "dev-fake-bot-token-do-not-use"
                )
            else:
                raise ValueError(
                    "TELEGRAM_BOT_TOKEN is required in production. "
                    "Get it from @BotFather in Telegram."
                )

        # STRIPE_SECRET_KEY: required in production. (Phase 6.3)
        if not self.stripe_secret_key:
            if is_dev:
                self.stripe_secret_key = "TEST"
            else:
                raise ValueError(
                    "STRIPE_SECRET_KEY is required in production. "
                    "Set to 'TEST' to start without Stripe, or "
                    "provide your Stripe secret key."
                )

        # STRIPE_WEBHOOK_SECRET: required in production. (Phase 6.3)
        if not self.stripe_webhook_secret:
            if is_dev:
                self.stripe_webhook_secret = "TEST"
            else:
                raise ValueError(
                    "STRIPE_WEBHOOK_SECRET is required in production. "
                    "Set to 'TEST' to start without Stripe, or "
                    "provide your Stripe webhook secret."
                )

        # STRIPE_SUCCESS_URL: required in production. (Phase 6.3)
        if not self.stripe_success_url:
            if is_dev:
                self.stripe_success_url = (
                    "http://localhost:3000/topup/success"
                )
            else:
                raise ValueError(
                    "STRIPE_SUCCESS_URL is required in production. "
                    "Set to 'TEST' to start without Stripe, or "
                    "provide your Telegram WebApp success page URL."
                )

        # STRIPE_CANCEL_URL: required in production. (Phase 6.3)
        if not self.stripe_cancel_url:
            if is_dev:
                self.stripe_cancel_url = (
                    "http://localhost:3000/topup/cancel"
                )
            else:
                raise ValueError(
                    "STRIPE_CANCEL_URL is required in production. "
                    "Set to 'TEST' to start without Stripe, or "
                    "provide your Telegram WebApp cancel page URL."
                )

        # WARNING-5: Disallow STRIPE_STUB in production.
        # is_stripe_stub means STRIPE_SECRET_KEY="TEST", which disables
        # webhook signature verification -- must never happen in production.
        if not is_dev and self.is_stripe_stub:
            raise ValueError(
                "STRIPE_SECRET_KEY cannot be 'TEST' in production. "
                "Provide your real Stripe secret key."
            )

        # CORS_ORIGINS: must not be wildcard in production (S-04).
        if not is_dev and self.cors_origins == "*":
            raise ValueError(
                "CORS_ORIGINS must not be '*' in production. "
                "Set to specific domain(s), e.g. "
                "'https://app.example.com'."
            )

        # CQ-02: commission_percent must be within valid range.
        # Prevents misconfiguration: negative commission or > 100%
        # would break integer math in purchase finalization
        # (paid_cents * commission_percent // 100).
        if not 0 <= self.commission_percent <= 100:
            raise ValueError(
                "commission_percent must be between 0 and 100, "
                f"got {self.commission_percent}"
            )

        # CQ-06: log_level must be a valid Python logging level.
        # In production, DEBUG is not allowed -- too noisy and may
        # leak sensitive data (request bodies, SQL queries, etc.).
        _valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self.log_level.upper() not in _valid_levels:
            raise ValueError(
                f"log_level must be one of {_valid_levels}, "
                f"got '{self.log_level}'"
            )
        if not is_dev and self.log_level.upper() == "DEBUG":
            raise ValueError(
                "log_level DEBUG is not allowed in production. "
                "Use INFO or higher."
            )

        return self

    # -- Pydantic Settings Config --
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def is_stripe_stub(self) -> bool:
        """True when Stripe is not configured (keys set to 'TEST')."""
        return self.stripe_secret_key.upper() == "TEST"


# Singleton: one Settings instance for the entire application.
settings = Settings()
