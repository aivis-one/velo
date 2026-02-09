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
from app.modules.users.router import router as users_router
from app.core.database import dispose_engine, get_engine
from app.core.exceptions import VeloError
from app.core.logging import setup_logging
from app.core.redis import close_redis, get_redis, init_redis
from app.modules.auth.router import router as auth_router
from app.modules.masters.models import MasterProfile


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

# ---------------------------------------------------------------------------
# Exception Handlers (TD-007)
# ---------------------------------------------------------------------------
@app.exception_handler(VeloError)
async def velo_error_handler(request: Request, exc: VeloError) -> JSONResponse:
    """Convert VeloError exceptions into proper HTTP responses."""
    logger.warning(
        "velo_error",
        status_code=exc.status_code,
        code=exc.code,
        message=exc.message,
        path=request.url.path,
        method=request.method,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.code, "message": exc.message},
    )


# ---------------------------------------------------------------------------
# CORS Middleware (TD-002)
# ---------------------------------------------------------------------------
_cors_origins = [o.strip() for o in settings.cors_origins.split(",")]
_allow_all = _cors_origins == ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=not _allow_all,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Health checks
# ---------------------------------------------------------------------------
_HEALTH_CHECK_TIMEOUT = 5.0


async def _check_db() -> str:
    """Check PostgreSQL connectivity."""
    try:
        async with asyncio.timeout(_HEALTH_CHECK_TIMEOUT):
            async with get_engine().connect() as conn:
                await conn.execute(text("SELECT 1"))
        return "ok"
    except Exception as e:
        logger.error("health_check_db_failed", error=str(e))
        return "error"


async def _check_redis() -> str:
    """Check Redis connectivity."""
    try:
        async with asyncio.timeout(_HEALTH_CHECK_TIMEOUT):
            redis = get_redis()
            pong = await redis.ping()  # type: ignore[misc]
            if pong:
                return "ok"
        return "error"
    except Exception as e:
        logger.error("health_check_redis_failed", error=str(e))
        return "error"


async def _check_health() -> dict[str, str]:
    """Check DB and Redis in parallel."""
    db_status, redis_status = await asyncio.gather(
        _check_db(),
        _check_redis(),
    )
    status = "ok" if db_status == "ok" and redis_status == "ok" else "degraded"
    return {"status": status, "db": db_status, "redis": redis_status}


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check — always returns 200."""
    return await _check_health()


@app.get("/ready")
async def ready() -> JSONResponse:
    """Readiness probe — returns 503 when degraded."""
    result = await _check_health()
    status_code = 200 if result["status"] == "ok" else 503
    return JSONResponse(content=result, status_code=status_code)


# ---------------------------------------------------------------------------
# Root
# ---------------------------------------------------------------------------
@app.get("/")
async def root() -> dict[str, str]:
    """API name and version."""
    return {"name": "VELO API", "version": "0.1.0"}
