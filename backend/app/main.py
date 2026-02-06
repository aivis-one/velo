# =============================================================================
# VELO Backend — Application Entry Point
# =============================================================================
#
# This is the main FastAPI application instance.
#
# RESPONSIBILITIES:
#   - Create FastAPI app with metadata
#   - Configure CORS (Cross-Origin Resource Sharing)
#   - Manage lifecycle (startup/shutdown of DB + Redis connections)
#   - Define root and health check endpoints
#   - Initialize structured logging
#
# HOW TO RUN:
#   make run  (or: uvicorn app.main:app --reload)
#
# ENDPOINTS:
#   GET /        -> API name + version
#   GET /health  -> DB + Redis connectivity check
# =============================================================================

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine
from app.core.logging import setup_logging
from app.core.redis import close_redis, get_redis, init_redis

logger = structlog.get_logger()


# ---------------------------------------------------------------------------
# Lifespan — startup and shutdown logic
# ---------------------------------------------------------------------------
# FastAPI's lifespan replaces the old @app.on_event("startup/shutdown").
# Everything before `yield` runs at startup; after yield — at shutdown.
# This ensures resources (Redis, DB pool) are properly initialized
# and cleaned up.
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifecycle: startup and shutdown."""
    # -- Startup --
    setup_logging(
        log_level=settings.log_level,
        json_logs=settings.app_env == "production",
    )
    await init_redis()
    logger.info(
        "app_started",
        env=settings.app_env,
        log_level=settings.log_level,
    )

    yield  # App is running, handling requests

    # -- Shutdown --
    await close_redis()
    await engine.dispose()
    logger.info("app_stopped")


# ---------------------------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="VELO API",
    description="Platform for wellness practice facilitators",
    version="0.1.0",
    lifespan=lifespan,
    # docs_url="/docs" is the default — Swagger UI.
    # Try it: http://localhost:8000/docs
)


# ---------------------------------------------------------------------------
# CORS Middleware
# ---------------------------------------------------------------------------
# CORS controls which websites can call our API. Without it, a browser
# running the Telegram WebApp would refuse to call our backend.
#
# For MVP: allow all origins. In production, restrict to:
#   - Telegram WebApp domain
#   - Our admin panel domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint — returns API name and version."""
    return {"name": "VELO API", "version": "0.1.0"}


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check — verifies DB and Redis connectivity.

    Returns 200 with status of each dependency.
    Used by Docker healthcheck, load balancers, and monitoring.

    Each check is independent: if Redis is down but DB is up,
    you see {"status": "degraded", "db": "ok", "redis": "error"}.
    """
    result: dict[str, str] = {
        "status": "ok",
        "db": "error",
        "redis": "error",
    }

    # Check PostgreSQL: "SELECT 1" is the lightest possible query.
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        result["db"] = "ok"
    except Exception as e:
        logger.error("health_check_db_failed", error=str(e))

    # Check Redis: PING returns PONG if alive.
    try:
        redis = get_redis()
        pong = await redis.ping()  # type: ignore[misc]
        if pong:
            result["redis"] = "ok"
    except Exception as e:
        logger.error("health_check_redis_failed", error=str(e))

    # Overall: "ok" only if ALL dependencies are healthy.
    if result["db"] != "ok" or result["redis"] != "ok":
        result["status"] = "degraded"

    return result
