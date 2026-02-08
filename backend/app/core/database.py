# =============================================================================
# VELO Backend — Database Connection
# =============================================================================
#
# LAZY ENGINE:
#   Engine is NOT created at import time. It's created on first call to
#   get_engine(). This prevents "Future attached to a different loop"
#   errors in pytest, where the event loop is created after module imports.
#
# DEPENDENCY INJECTION:
#   get_db_session()  — read-write: commits on success, rollback on error.
#   get_db_reader()   — read-only: always rolls back (TD-008).
# =============================================================================

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""


# ---------------------------------------------------------------------------
# Lazy engine — created on first access, not at import time
# ---------------------------------------------------------------------------
_engine: AsyncEngine | None = None


def get_engine() -> AsyncEngine:
    """Get or create the async engine (singleton)."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.database_url,
            echo=False,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=1800,
        )
    return _engine


async def dispose_engine() -> None:
    """Dispose the engine and reset singleton. Used in shutdown/tests."""
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Get a session factory bound to the current engine."""
    return async_sessionmaker(
        bind=get_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Transactional session for write operations (auto-commit/rollback)."""
    factory = get_session_factory()
    session = factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_db_reader() -> AsyncGenerator[AsyncSession, None]:
    """Read-only session — always rolls back (TD-008)."""
    factory = get_session_factory()
    session = factory()
    try:
        yield session
    finally:
        await session.rollback()
        await session.close()
