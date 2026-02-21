# =============================================================================
# VELO Backend -- Application Entry Point (updated Phase 6.6)
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
from app.core.middleware import TraceIdMiddleware
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
from app.modules.payments.router import router as payments_router  # Phase 6.3
from app.modules.payments.webhook_router import webhook_router     # Phase 6.3
from app.modules.payments.purchase_router import (                 # Phase 6.4
    router as purchase_router,
    purchases_user_router,                                         # Frontend Backlog
)
from app.modules.withdrawals.router import (                       # Phase 6.6
    router as withdrawals_router,
)
# NOTE: admin/withdrawals router is included via admin_router (admin/router.py).
# Do NOT register it separately here to avoid duplicate endpoints (BUG-07).


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
app.include_router(payments_router)               # Phase 6.3
app.include_router(webhook_router)                # Phase 6.3
app.include_router(purchase_router)               # Phase 6.4
app.include_router(purchases_user_router)         # Frontend Backlog
app.include_router(withdrawals_router)            # Phase 6.6

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


# L-06: global handler for unexpected (non-VeloError) exceptions.
# Without this, unhandled exceptions leak stack traces to the client
# as FastAPI's default 500 HTML/text response.
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for unexpected exceptions -- return generic 500 JSON."""
    logger.error(
        "unhandled_exception",
        exc_type=type(exc).__name__,
        exc_msg=str(exc),
        path=request.url.path,
    )
    return JSONResponse(
        status_code=500,
        content={"error": "internal", "message": "Internal server error"},
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

# TraceIdMiddleware (L-03): injects X-Trace-Id into every response.
app.add_middleware(TraceIdMiddleware)


# ---------------------------------------------------------------------------
# Root & Health Endpoints
# ---------------------------------------------------------------------------
@app.get("/")
async def root() -> dict:
    """API root -- name and version."""
    return {"name": "VELO API", "version": "0.1.0"}


@app.get("/health")
async def health() -> dict:
    """Health check -- always 200, reports component status."""
    db_status = "ok"
    redis_status = "ok"

    # Check database.
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "degraded"

    # Check Redis.
    try:
        redis = get_redis()
        await redis.ping()
    except Exception:
        redis_status = "degraded"

    overall = "ok" if db_status == "ok" and redis_status == "ok" else "degraded"
    return {"status": overall, "db": db_status, "redis": redis_status}


@app.get("/ready")
async def ready() -> JSONResponse:
    """Readiness probe -- 503 if any component is degraded."""
    h = await health()
    if h["db"] != "ok" or h["redis"] != "ok":
        return JSONResponse(status_code=503, content=h)
    return JSONResponse(status_code=200, content=h)
