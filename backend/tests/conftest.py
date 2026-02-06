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
# PHASES:
#   Phase 0.1: Basic client fixture (no DB).
#   Phase 0.3: Will add DB fixtures (async session, test database).
# =============================================================================

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

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
