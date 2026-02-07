# =============================================================================
# VELO Backend — Database Connection
# =============================================================================
#
# HOW IT WORKS:
#   SQLAlchemy needs two things to talk to PostgreSQL:
#
#   1. Engine — the "connection pool". It maintains a pool of open connections
#      to the database, reusing them instead of opening a new one per request.
#      Think of it as a phone switchboard: requests come in, get assigned an
#      available line, and release it when done.
#
#   2. Session — a "unit of work". Each request gets its own session.
#      All queries within one request share the same session (and transaction).
#      If something fails, the entire session rolls back — no half-done changes.
#
# ASYNC:
#   We use AsyncEngine + AsyncSession because FastAPI is async.
#   Sync SQLAlchemy would block the event loop — one slow query would freeze
#   ALL other requests. Async lets other requests proceed while waiting for DB.
#
# DEPENDENCY INJECTION:
#   FastAPI endpoints declare `session: AsyncSession = Depends(get_db_session)`
#   and FastAPI automatically creates a session, passes it in, and cleans up
#   after the request — even if an exception occurs.
#
# TWO SESSION PROVIDERS (TD-008):
#   get_db_session()  — read-write: commits on success, rollback on error.
#   get_db_reader()   — read-only: always rolls back (no round-trip for commit).
#   Use get_db_reader() for GET endpoints that only SELECT data.
#
# BASE:
#   All SQLAlchemy models inherit from Base. Alembic reads Base.metadata
#   to detect schema changes and generate migrations automatically.
# =============================================================================

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


# ---------------------------------------------------------------------------
# Declarative Base — parent class for all ORM models
# ---------------------------------------------------------------------------
# Every model (User, Practice, Booking, etc.) inherits from this.
# Base.metadata holds the schema description — Alembic uses it to
# generate migrations by comparing metadata vs actual DB state.
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""


# ---------------------------------------------------------------------------
# Engine — connection pool to PostgreSQL
# ---------------------------------------------------------------------------
# echo=False: don't print every SQL query to stdout.
# pool_size=10: keep 10 connections open and ready.
# max_overflow=20: allow up to 20 extra under heavy load.
#   Total max = pool_size + max_overflow = 30.
#   PostgreSQL default max_connections = 100, well within limits.
engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_size=10,
    max_overflow=20,
)

# ---------------------------------------------------------------------------
# Session factory — creates new sessions
# ---------------------------------------------------------------------------
# expire_on_commit=False: after commit, objects stay usable without
#   re-querying the database. Without this, accessing user.name after
#   commit would trigger a lazy load — which fails in async context.
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional database session for write operations.

    Usage in FastAPI endpoints:
        @router.post("/users")
        async def create_user(
            session: AsyncSession = Depends(get_db_session),
        ):
            session.add(User(...))
            # commit happens automatically after endpoint returns

    The session is automatically committed on success and rolled back
    on exception. Finally, it's always closed to return the connection
    to the pool.
    """
    session = async_session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_db_reader() -> AsyncGenerator[AsyncSession, None]:
    """Provide a read-only database session for queries. (TD-008)

    Usage in FastAPI endpoints:
        @router.get("/users")
        async def list_users(
            session: AsyncSession = Depends(get_db_reader),
        ):
            result = await session.execute(select(User))
            ...

    Unlike get_db_session(), this never commits — it rolls back instead.
    This avoids an unnecessary round-trip to PostgreSQL on every GET request.
    The rollback is essentially free: it just tells the driver
    "discard this transaction, nothing was written".
    """
    session = async_session_factory()
    try:
        yield session
    finally:
        await session.rollback()
        await session.close()
