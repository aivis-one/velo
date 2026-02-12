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
from app.modules.admin.router import router as admin_router
from app.modules.auth.router import router as auth_router
from app.modules.masters.router import router as masters_router
from app.modules.users.router import router as users_router
from app.modules.reports.router import router as reports_router
from app.modules.practices.router import router as practices_router
from app.modules.bookings.router import (
    practices_attendance_router,  # Phase 5.4
    router as bookings_router,
)
from app.modules.waitlist.router import (  # Phase 5.3
    practices_waitlist_router,
    waitlist_router,
)


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
app.include_router(admin_router)
app.include_router(reports_router)
app.include_router(practices_router)
app.include_router(bookings_router)
app.include_router(practices_waitlist_router)    # Phase 5.3
app.include_router(waitlist_router)               # Phase 5.3
app.include_router(practices_attendance_router)   # Phase 5.4

# ---------------------------------------------------------------------------
# Exception Handlers (TD-007)
# ---------------------------------------------------------------------------
@app.exception_handler(VeloError)
async def velo_error_handler(request: Request, exc: VeloError) -> JSONResponse:
    """Convert VeloError exceptions into proper HTTP responses."""
    if exc.status_code >= 500:
        logger.error(
            "unhandled_velo_error",
            status_code=exc.status_code,
            code=exc.code,
            message=exc.message,
            path=request.url.path,
        )
    else:
        logger.warning(
            "velo_error",
            status_code=exc.status_code,
            code=exc.code,
            message=exc.message,
            path=request.url.path,
        )

    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.code, "message": exc.message},
    )


# ---------------------------------------------------------------------------
# CORS
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
# Root
# ---------------------------------------------------------------------------
@app.get("/")
async def root() -> dict:
    """API info -- name and version."""
    return {"name": "VELO API", "version": "0.1.0"}


# ---------------------------------------------------------------------------
# Health / Ready
# ---------------------------------------------------------------------------
@app.get("/health")
async def health() -> dict:
    """Health check -- always returns 200.

    Reports DB and Redis connectivity status. Used by monitoring tools
    that only care "is the process alive?".
    """
    result: dict = {"status": "ok", "db": "unknown", "redis": "unknown"}

    # Check DB.
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        result["db"] = "ok"
    except Exception:
        result["db"] = "error"
        result["status"] = "degraded"

    # Check Redis.
    try:
        redis = get_redis()
        await redis.ping()
        result["redis"] = "ok"
    except Exception:
        result["redis"] = "error"
        result["status"] = "degraded"

    return result


@app.get("/ready")
async def ready() -> JSONResponse:
    """Readiness probe -- returns 503 if any dependency is down.

    Used by load balancers to decide whether to route traffic here.
    """
    checks: dict = {"db": "unknown", "redis": "unknown"}
    all_ok = True

    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["db"] = "ok"
    except Exception:
        checks["db"] = "error"
        all_ok = False

    try:
        redis = get_redis()
        pong = await asyncio.wait_for(redis.ping(), timeout=2.0)
        checks["redis"] = "ok" if pong else "error"
        if not pong:
            all_ok = False
    except Exception:
        checks["redis"] = "error"
        all_ok = False

    status_code = 200 if all_ok else 503
    return JSONResponse(
        status_code=status_code,
        content={"status": "ok" if all_ok else "degraded", **checks},
    )
