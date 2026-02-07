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
#   - Register exception handlers for VeloError hierarchy
#   - Define root, health, and readiness endpoints
#   - Initialize structured logging
#
# HOW TO RUN:
#   make run  (or: uvicorn app.main:app --reload)
#
# ENDPOINTS:
#   GET /        -> API name + version
#   GET /health  -> DB + Redis connectivity check (always 200)
#   GET /ready   -> Readiness probe (503 if degraded)
# =============================================================================

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.requests import Request

from app.core.config import settings
from app.core.database import engine
from app.core.exceptions import VeloError
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
#
# TD-009: try/finally ensures engine.dispose() runs even if init_redis()
# fails. Without it, the DB connection pool would leak on startup errors.
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifecycle: startup and shutdown."""
    # -- Startup --
    setup_logging(
        log_level=settings.log_level,
        json_logs=settings.app_env == "production",
    )

    try:
        await init_redis()
        logger.info(
            "app_started",
            env=settings.app_env,
            log_level=settings.log_level,
        )

        yield  # App is running, handling requests

    finally:
        # -- Shutdown (or startup failure cleanup) --
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
# Exception Handlers (TD-007)
# ---------------------------------------------------------------------------
# VeloError carries status_code + machine-readable code.
# Without this handler, any `raise NotFoundError(...)` would return 500.
# Now it returns the correct HTTP status (404, 403, 409, etc.)
@app.exception_handler(VeloError)
async def velo_error_handler(request: Request, exc: VeloError) -> JSONResponse:
    """Convert VeloError exceptions into proper HTTP responses."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.code,
            "message": exc.message,
        },
    )


# ---------------------------------------------------------------------------
# CORS Middleware (TD-002)
# ---------------------------------------------------------------------------
# CORS controls which websites can call our API. Without it, a browser
# running the Telegram WebApp would refuse to call our backend.
#
# TD-002: allow_credentials=True is incompatible with allow_origins=["*"].
# In development (CORS_ORIGINS=*), we disable credentials.
# In production (specific origins), we enable credentials.
_cors_origins = settings.cors_origins.split(",")
_allow_all = _cors_origins == ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=not _allow_all,  # TD-002: no credentials with wildcard
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


async def _check_health() -> dict[str, str]:
    """Check DB and Redis connectivity. Shared by /health and /ready."""
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


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check — verifies DB and Redis connectivity.

    Always returns 200 with status of each dependency.
    Used by monitoring tools and dashboards.

    Each check is independent: if Redis is down but DB is up,
    you see {"status": "degraded", "db": "ok", "redis": "error"}.
    """
    return await _check_health()


@app.get("/ready")
async def ready() -> JSONResponse:
    """Readiness probe — returns 503 if any dependency is down. (TD-003)

    Used by load balancers and Docker healthchecks to decide
    whether to route traffic to this instance.

    Unlike /health (always 200), /ready returns:
      200 — all dependencies healthy, ready to serve
      503 — one or more dependencies down, don't route traffic here
    """
    result = await _check_health()

    if result["status"] != "ok":
        return JSONResponse(status_code=503, content=result)

    return JSONResponse(status_code=200, content=result)
