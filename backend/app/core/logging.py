# =============================================================================
# VELO Backend -- Structured Logging (structlog)
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
# FILTERING (TD-011):
#   make_filtering_bound_logger(level) creates a wrapper class that
#   drops events below the configured level BEFORE processing. This
#   is more efficient than filtering in the processor chain.
#
# IDEMPOTENCY (TD-012):
#   setup_logging() is guarded by _configured flag. If called twice
#   (e.g., app startup + test setup), the second call is a no-op.
#   This prevents cache_logger_on_first_use from locking in a wrong
#   config if structlog.get_logger() was called between two setups.
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

# Guard flag for idempotency (TD-012).
_configured: bool = False


def setup_logging(log_level: str = "DEBUG", json_logs: bool = False) -> None:
    """Configure structlog for the application.

    Args:
        log_level: Minimum severity to log (DEBUG/INFO/WARNING/ERROR).
        json_logs: True = JSON output (production), False = pretty (dev).
    """
    global _configured
    if _configured:
        return
    _configured = True

    # Convert string level to logging constant: "DEBUG" -> logging.DEBUG
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
            *shared_processors,
            # Format exceptions as readable tracebacks.
            structlog.processors.format_exc_info,
            # Final step: render to JSON or console.
            renderer,
        ],
        context_class=dict,
        # TD-011: make_filtering_bound_logger drops events below
        # the configured level at the binding stage -- before any
        # processor runs. Much more efficient than stdlib filtering.
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.PrintLoggerFactory(
            file=sys.stdout,
        ),
        # Cache the logger configuration for performance.
        cache_logger_on_first_use=True,
    )

    # Also configure stdlib logging (used by uvicorn, sqlalchemy, etc.)
    # so their output respects the same level.
    logging.basicConfig(
        format="%(message)s",
        level=level,
        stream=sys.stdout,
    )
