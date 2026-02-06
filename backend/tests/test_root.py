# =============================================================================
# Test: Root Endpoint
# =============================================================================
#
# This is the simplest possible test — it verifies that the server starts
# and the root endpoint returns the expected response.
#
# WHY START WITH A TEST?
#   Having at least one test from day one means:
#   1. CI/CD pipeline has something to run (validates the setup works)
#   2. pre-commit hooks can verify pytest is configured correctly
#   3. You establish the habit: every feature starts with a test
# =============================================================================

from httpx import AsyncClient


async def test_root_returns_api_info(client: AsyncClient) -> None:
    """Root endpoint should return API name and version."""
    response = await client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "VELO API"
    assert data["version"] == "0.1.0"
