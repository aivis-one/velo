# =============================================================================
# VELO Backend — Pytest Configuration & Fixtures
# =============================================================================
#
# WHAT IS conftest.py?
#   A special pytest file that provides "fixtures" — reusable setup/teardown
#   logic shared across all tests. Pytest auto-discovers it (no imports needed).
#
# WHAT ARE FIXTURES?
#   Think of them as "prepared ingredients" for your tests.
#   Instead of each test creating its own HTTP client, database connection, etc.,
#   fixtures do it once and inject the result into any test that asks for it.
#
# EXAMPLE:
#   async def test_root(client: AsyncClient) -> None:
#       response = await client.get("/")
#       assert response.status_code == 200
#
#   Here `client` is a fixture defined below — pytest sees the parameter name,
#   finds the matching fixture, runs it, and passes the result to the test.
#
# FIXTURES:
#   client     — Async HTTP client for testing FastAPI endpoints (in-memory).
#   db_session — Direct async DB session for test setup/teardown (TD-020).
# =============================================================================

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.main import app


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client for testing FastAPI endpoints.

    Uses httpx.AsyncClient with ASGITransport — this means requests
    go directly to FastAPI in memory, no real HTTP server is started.
    Tests run fast because there's no network overhead.

    Usage in tests:
        async def test_something(client: AsyncClient) -> None:
            response = await client.get("/some-endpoint")
            assert response.status_code == 200
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Direct database session for test setup and teardown.

    Provides raw AsyncSession for operations that bypass the API layer,
    such as deactivating a user or verifying DB state after an endpoint call.

    Unlike get_db_session() (which auto-commits), this session requires
    explicit commit — giving tests full control over transactions.

    Usage in tests:
        async def test_something(db_session: AsyncSession) -> None:
            stmt = update(User).where(...).values(is_active=False)
            await db_session.execute(stmt)
            await db_session.commit()
    """
    session = async_session_factory()
    try:
        yield session
    finally:
        await session.close()
