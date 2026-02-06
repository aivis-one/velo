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
# =============================================================================

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
    # Format: postgresql+asyncpg://user:pass@host:port/dbname
    database_url: str = "postgresql+asyncpg://velo:velo@localhost:5432/velo"

    # -- Redis --
    redis_url: str = "redis://localhost:6379/0"

    # -- Security --
    secret_key: str = "change-me-in-production-use-secrets-token-urlsafe"

    # -- Logging --
    log_level: str = "DEBUG"

    # -- Pydantic Settings Config --
    # Tells pydantic-settings WHERE to read env vars from.
    # env_file=".env" reads .env in the working directory.
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
