# =============================================================================
# VELO Backend — Test Fixtures
# =============================================================================
#
# Solves three problems that broke tests before:
#   1. Event loop — single loop for all tests (no "Future attached to different loop")
#   2. Lifespan — init_redis() and engine are ready before tests run
#   3. Migrations — tables exist before tests run (alembic upgrade head)
#
# 7.1 fix: db_session rolls back before closing.
#   If a test crashes mid-operation and leaves uncommitted state in the
#   session (e.g. flushed but not committed), the rollback ensures that
#   state is discarded and does not bleed into the next test.
#   Tests that need data to persist use explicit session.commit() calls,
#   which are unaffected by the rollback (only uncommitted state is cleared).
# =============================================================================

import subprocess
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import dispose_engine, get_session_factory
from app.core.redis import close_redis, init_redis
from app.main import app


@pytest.fixture(scope="session", autouse=True)
async def setup_infrastructure():
    """Initialize Redis, run migrations, and clean up after all tests.

    Runs ONCE before any test. Alembic is called as subprocess because
    its env.py uses asyncio.run() which can't nest inside pytest's loop.
    """
    # Run Alembic migrations (ensures tables exist).
    result = subprocess.run(
        ["python", "-m", "alembic", "upgrade", "head"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Alembic migration failed:\n{result.stderr}\n{result.stdout}"
        )

    # Initialize Redis client.
    await init_redis()

    yield

    # Cleanup.
    await close_redis()
    await dispose_engine()


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client — requests go directly to FastAPI in memory."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Direct database session for test setup/assertions.

    7.1 fix: rolls back before closing to discard any uncommitted state
    left behind by a failing test. Prevents state from bleeding into
    subsequent tests that share the same DB connection pool.

    Tests that need data to persist must call session.commit() explicitly —
    those commits are permanent and unaffected by this rollback.
    """
    factory = get_session_factory()
    session = factory()
    try:
        yield session
    finally:
        await session.rollback()  # discard any uncommitted state (7.1)
        await session.close()
