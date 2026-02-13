# =============================================================================
# VELO Backend -- Application Configuration (updated Phase 6.3)
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

    # -- Sessions --
    # How long a session token lives in Redis (days).
    session_ttl_days: int = 30

    # -- Logging --
    log_level: str = "DEBUG"

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
        # Value "TEST" is accepted as a stub -- app starts but
        # topup endpoint returns 503 (checked in stripe.py).
        if not self.stripe_secret_key:
            if is_dev:
                self.stripe_secret_key = (
                    "sk_test_fake_dev_key_do_not_use"
                )
            else:
                raise ValueError(
                    "STRIPE_SECRET_KEY is required in production. "
                    "Set to 'TEST' to start without Stripe, or "
                    "provide a real key from Stripe Dashboard."
                )

        # STRIPE_WEBHOOK_SECRET: required in production. (Phase 6.3)
        if not self.stripe_webhook_secret:
            if is_dev:
                self.stripe_webhook_secret = (
                    "whsec_fake_dev_secret_do_not_use"
                )
            else:
                raise ValueError(
                    "STRIPE_WEBHOOK_SECRET is required in production. "
                    "Set to 'TEST' to start without Stripe, or "
                    "provide a real key from Stripe Dashboard -> Webhooks."
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
