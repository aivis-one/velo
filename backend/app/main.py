# =============================================================================
# VELO Backend — Application Entry Point
# =============================================================================
#
# ENDPOINTS:
#   GET /        -> API name + version
#   GET /health  -> DB + Redis connectivity check (always 200)
#   GET /ready   -> Readiness probe (503 if degraded)
# =============================================================================

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.requests import Request

from app.core.config import settings
from app.core.database import dispose_engine, get_engine
from app.core.exceptions import VeloError
from app.core.logging import setup_logging
from app.core.redis import close_redis, get_redis, init_redis
from app.modules.auth.router import router as auth_router
from app.modules.masters.router import router as masters_router
from app.modules.users.router import router as users_router


logger = structlog.get_logger()


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifecycle: startup and shutdown."""
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
        yield
    finally:
        await close_redis()
        await dispose_engine()
        logger.info("app_stopped")


# ---------------------------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="VELO API",
    description="Platform for wellness practice facilitators",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(masters_router)

# ---------------------------------------------------------------------------
# Exception Handlers (TD-007)
# ---------------------------------------------------------------------------
@app.exception_handler(VeloError)
async def velo_error_handler(request: Request, exc: VeloError) -> JSONResponse:
    """Convert VeloError exceptions into proper HTTP responses."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Root
# ---------------------------------------------------------------------------
@app.get("/")
async def root() -> dict:
    """API info endpoint."""
    return {
        "api": "VELO",
        "version": "0.1.0",
        "docs": "/docs",
    }


# ---------------------------------------------------------------------------
# Health Checks
# ---------------------------------------------------------------------------
@app.get("/health")
async def health() -> JSONResponse:
    """Health check — always returns 200, reports component status."""
    db_ok = True
    redis_ok = True

    # Check database.
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        db_ok = False

    # Check Redis.
    try:
        redis = await get_redis()
        await redis.ping()
    except Exception:
        redis_ok = False

    return JSONResponse(
        content={
            "status": "ok" if (db_ok and redis_ok) else "degraded",
            "db": "ok" if db_ok else "error",
            "redis": "ok" if redis_ok else "error",
        },
        status_code=200,
    )


@app.get("/ready")
async def ready() -> JSONResponse:
    """Readiness probe — returns 503 if any component is down."""
    checks: dict[str, bool] = {}

    # Database.
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await asyncio.wait_for(conn.execute(text("SELECT 1")), timeout=2.0)
        checks["db"] = True
    except Exception:
        checks["db"] = False

    # Redis.
    try:
        redis = await get_redis()
        await asyncio.wait_for(redis.ping(), timeout=2.0)
        checks["redis"] = True
    except Exception:
        checks["redis"] = False

    all_ok = all(checks.values())
    return JSONResponse(
        content={
            "status": "ok" if all_ok else "degraded",
            **{k: "ok" if v else "error" for k, v in checks.items()},
        },
        status_code=200 if all_ok else 503,
    )
