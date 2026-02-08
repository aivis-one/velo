# =============================================================================
# VELO Backend — Application Configuration
# =============================================================================
#
# HOW IT WORKS:
#   1. pydantic-settings reads your .env file
#   2. Each field here maps to an environment variable (case-insensitive)
#   3. Pydantic validates types: if DATABASE_URL is missing or malformed,
#      the app crashes at startup with a clear error — not at runtime
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
#   have no defaults — the app refuses to start without a proper .env.
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
    # No default in production — app won't start without it. (TD-001)
    secret_key: str = ""

    # -- Telegram --
    # Bot token from BotFather. Required for initData validation.
    # Dev default is a fake token — HMAC won't match real Telegram data,
    # but tests mock validation anyway. (P-4)
    telegram_bot_token: str = "dev-fake-bot-token-do-not-use"

    # -- Sessions --
    # How long a session token lives in Redis (days).
    session_ttl_days: int = 30

    # -- Logging --
    log_level: str = "DEBUG"

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
                self.database_url = "postgresql+asyncpg://velo:velo@localhost:5433/velo"
            else:
                raise ValueError(
                    "DATABASE_URL is required in production. " "Set it in .env file."
                )

        # SECRET_KEY: default only in dev (TD-001)
        if not self.secret_key:
            if is_dev:
                self.secret_key = "dev-only-insecure-key-do-not-use-in-production"
            else:
                raise ValueError(
                    "SECRET_KEY is required in production. "
                    'Generate with: python -c "import secrets; '
                    'print(secrets.token_urlsafe(64))"'
                )

        # TELEGRAM_BOT_TOKEN: required in production for initData validation.
        if not self.telegram_bot_token and not is_dev:
            raise ValueError(
                "TELEGRAM_BOT_TOKEN is required in production. "
                "Get it from @BotFather in Telegram."
            )

        return self

    # -- Pydantic Settings Config --
    # Tells pydantic-settings WHERE to read env vars from.
    # env_file= ".env" reads .env in the working directory.
    # case_sensitive=False: DATABASE_URL and database_url both work.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Singleton: one Settings instance for the entire application.
# Every module imports `settings` and uses the same validated config.
#
# Usage:
#   from app.core.config import settings
#   print(settings.database_url)
settings = Settings()
