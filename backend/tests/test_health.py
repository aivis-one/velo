# =============================================================================
# VELO Backend — Health Check Tests
# =============================================================================
#
# Success tests use real DB + Redis (setup_infrastructure ensures they're up).
# Failure tests mock get_engine/get_redis to simulate degraded states.
# =============================================================================

from unittest.mock import MagicMock, patch

from httpx import AsyncClient


# ---------------------------------------------------------------------------
# /health endpoint — always 200
# ---------------------------------------------------------------------------


async def test_health_all_ok(client: AsyncClient) -> None:
    """Health check returns ok when real DB and Redis are available."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["db"] == "ok"
    assert data["redis"] == "ok"


async def test_health_db_down(client: AsyncClient) -> None:
    """Health reports degraded when DB is unreachable."""
    mock_engine = MagicMock()
    mock_engine.connect.side_effect = ConnectionError("DB down")

    with patch("app.main.get_engine", return_value=mock_engine):
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "degraded"
    assert data["db"] == "error"
    assert data["redis"] == "ok"


async def test_health_redis_down(client: AsyncClient) -> None:
    """Health reports degraded when Redis is unreachable."""
    with patch(
        "app.main.get_redis",
        side_effect=RuntimeError("Redis not init"),
    ):
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "degraded"
    assert data["db"] == "ok"
    assert data["redis"] == "error"


# ---------------------------------------------------------------------------
# /ready endpoint — returns 503 when degraded
# ---------------------------------------------------------------------------


async def test_ready_all_ok(client: AsyncClient) -> None:
    """Readiness probe returns 200 when all dependencies are healthy."""
    response = await client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


async def test_ready_returns_503_when_degraded(client: AsyncClient) -> None:
    """Readiness probe returns 503 when DB is down."""
    mock_engine = MagicMock()
    mock_engine.connect.side_effect = ConnectionError("DB down")

    with patch("app.main.get_engine", return_value=mock_engine):
        response = await client.get("/ready")

    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "degraded"
