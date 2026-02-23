# =============================================================================
# VELO Backend -- Application Entry Point (updated Phase 7.3)
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
from app.modules.promos.router import router as promos_router      # Phase 6.7

# Model imports for Alembic and relationship resolution.
from app.modules.promos.models import Promo  # noqa: F401  # Phase 6.7
from app.modules.notifications.models import Notification, NotificationDelivery  # noqa: F401  # Phase 7.1

# Notification processor (Phase 7.2).
from app.modules.notifications.processor import run_processor  # Phase 7.2

# Notification templates (Phase 7.3).
from app.modules.notifications.template_engine import load_templates  # Phase 7.3


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

    processor_task: asyncio.Task | None = None
    try:
        await init_redis()

        # Phase 7.3: Load notification templates from YAML files.
        template_count = load_templates()
        logger.info("notification_templates_loaded", count=template_count)

        # Start notification processor as background task (Phase 7.2).
        processor_task = asyncio.create_task(
            run_processor(), name="notification_processor",
        )

        logger.info(
            "app_started",
            env=settings.app_env,
            log_level=settings.log_level,
        )
        yield
    finally:
        # Stop notification processor.
        if processor_task is not None and not processor_task.done():
            processor_task.cancel()
            try:
                await processor_task
            except asyncio.CancelledError:
                pass

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
app.include_router(promos_router)                 # Phase 6.7

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
# Middleware
# ---------------------------------------------------------------------------
app.add_middleware(TraceIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Root + Health Checks
# ---------------------------------------------------------------------------
@app.get("/")
async def root() -> dict:
    """API root -- name, version, environment."""
    return {
        "name": "VELO API",
        "version": "0.1.0",
        "env": settings.app_env,
    }


@app.get("/health")
async def health() -> dict:
    """Health check -- verify DB and Redis connectivity.

    Always returns 200 with component status.
    """
    result = {"status": "ok", "database": "ok", "redis": "ok"}

    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as exc:
        result["database"] = f"error: {exc}"
        result["status"] = "degraded"

    try:
        redis = get_redis()
        await redis.ping()
    except Exception as exc:
        result["redis"] = f"error: {exc}"
        result["status"] = "degraded"

    return result


@app.get("/ready")
async def ready() -> JSONResponse:
    """Readiness probe -- 200 if all systems go, 503 if degraded."""
    h = await health()
    status_code = 200 if h["status"] == "ok" else 503
    return JSONResponse(content=h, status_code=status_code)
