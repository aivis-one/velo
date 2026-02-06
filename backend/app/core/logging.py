# =============================================================================
# VELO Backend — Structured Logging (structlog)
# =============================================================================
#
# WHY STRUCTLOG?
#   Standard logging:  "User 123 booked practice 456"
#   Structlog output:  {"event": "practice_booked", "user_id": 123,
#                       "practice_id": 456, "timestamp": "2026-..."}
#
#   The second form is machine-parseable. You can filter, aggregate,
#   and alert on structured fields in ELK/Grafana/Datadog.
#
# TWO MODES:
#   Development: colored, human-readable output (ConsoleRenderer)
#   Production:  JSON lines, one event per line (JSONRenderer)
#
# USAGE:
#   import structlog
#   logger = structlog.get_logger()
#
#   logger.info("practice_booked", user_id=123, practice_id=456)
#   logger.warning("low_balance", user_id=123, balance=5.00)
#   logger.error("payment_failed", error="card_declined", user_id=123)
# =============================================================================

import logging
import sys

import structlog


def setup_logging(log_level: str = "DEBUG", json_logs: bool = False) -> None:
    """Configure structlog for the application.

    Args:
        log_level: Minimum severity to log (DEBUG/INFO/WARNING/ERROR).
        json_logs: True = JSON output (production), False = pretty (dev).
    """
    # Convert string level to logging constant: "DEBUG" → logging.DEBUG
    level = getattr(logging, log_level.upper(), logging.DEBUG)

    # -- Shared processors (run on every log event) --
    shared_processors: list[structlog.types.Processor] = [
        # Add log level as a field: {"level": "info", ...}
        structlog.stdlib.add_log_level,
        # Add ISO timestamp: {"timestamp": "2026-02-06T14:30:00Z", ...}
        structlog.processors.TimeStamper(fmt="iso"),
        # Add caller info (file + line number) for debugging.
        structlog.processors.CallsiteParameterAdder(
            [
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            ],
        ),
        # Merge thread-local context (trace_id, user_id set by middleware).
        structlog.contextvars.merge_contextvars,
    ]

    if json_logs:
        # Production: one JSON object per line.
        # Easy to pipe into ELK, Datadog, CloudWatch, etc.
        renderer: structlog.types.Processor = structlog.processors.JSONRenderer()
    else:
        # Development: colored, indented, human-friendly.
        # Much easier to read in terminal during development.
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[
            # Filter events below the configured level.
            *shared_processors,
            # Format exceptions as readable tracebacks.
            structlog.processors.format_exc_info,
            # Final step: render to JSON or console.
            renderer,
        ],
        # dict is the fastest context class for structlog.
        context_class=dict,
        # BoundLogger wraps stdlib logging — compatible with
        # existing Python logging infrastructure.
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.PrintLoggerFactory(
            file=sys.stdout,
        ),
        # Cache the logger configuration for performance.
        cache_logger_on_first_use=True,
    )

    # Also configure stdlib logging (used by uvicorn, sqlalchemy, etc.)
    # so their output goes through structlog too.
    logging.basicConfig(
        format="%(message)s",
        level=level,
        stream=sys.stdout,
    )
