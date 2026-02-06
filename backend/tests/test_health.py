# =============================================================================
# Test: Health Check Endpoint
# =============================================================================
#
# We MOCK database and Redis so tests run WITHOUT Docker.
# CI/CD pipeline doesn't have PostgreSQL or Redis running.
# =============================================================================

from unittest.mock import AsyncMock, MagicMock, patch

from httpx import AsyncClient


async def test_health_all_ok(client: AsyncClient) -> None:
    """Health check returns 'ok' when both DB and Redis are healthy."""
    # Create a mock connection that can execute queries.
    mock_conn = AsyncMock()

    # Create a mock engine whose .connect() works as async CM.
    mock_engine = MagicMock()
    mock_engine.connect.return_value.__aenter__ = AsyncMock(
        return_value=mock_conn,
    )
    mock_engine.connect.return_value.__aexit__ = AsyncMock(
        return_value=False,
    )

    # Mock Redis client with ping() returning True.
    mock_redis = AsyncMock()
    mock_redis.ping.return_value = True

    with (
        patch("app.main.engine", mock_engine),
        patch("app.main.get_redis", return_value=mock_redis),
    ):
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["db"] == "ok"
    assert data["redis"] == "ok"


async def test_health_db_down(client: AsyncClient) -> None:
    """Health check returns 'degraded' when DB is unreachable."""
    mock_engine = MagicMock()
    mock_engine.connect.side_effect = ConnectionError("DB down")

    mock_redis = AsyncMock()
    mock_redis.ping.return_value = True

    with (
        patch("app.main.engine", mock_engine),
        patch("app.main.get_redis", return_value=mock_redis),
    ):
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "degraded"
    assert data["db"] == "error"
    assert data["redis"] == "ok"


async def test_health_redis_down(client: AsyncClient) -> None:
    """Health check returns 'degraded' when Redis is unreachable."""
    mock_conn = AsyncMock()

    mock_engine = MagicMock()
    mock_engine.connect.return_value.__aenter__ = AsyncMock(
        return_value=mock_conn,
    )
    mock_engine.connect.return_value.__aexit__ = AsyncMock(
        return_value=False,
    )

    with (
        patch("app.main.engine", mock_engine),
        patch(
            "app.main.get_redis",
            side_effect=RuntimeError("Redis not init"),
        ),
    ):
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "degraded"
    assert data["db"] == "ok"
    assert data["redis"] == "error"
