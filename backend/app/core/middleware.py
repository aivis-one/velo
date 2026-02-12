# =============================================================================
# VELO Backend -- ASGI Middleware
# =============================================================================
#
# Pure ASGI middleware -- no BaseHTTPMiddleware wrapper. This guarantees
# that structlog contextvars work reliably without TaskGroup isolation
# issues that BaseHTTPMiddleware can introduce.
#
# TRACE ID (Pre-6.1):
#   Every HTTP request gets a trace_id:
#     - From X-Trace-ID header (if provided by client/load balancer)
#     - Or auto-generated uuid4
#   The trace_id is:
#     1. Bound to structlog contextvars -> appears in every log line
#     2. Returned in X-Trace-ID response header -> client can correlate
#   In Phase 6 (Payments), trace_id will link AuditLog entries to
#   application logs for financial operation tracing.
# =============================================================================

from uuid import uuid4

import structlog
from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Receive, Scope, Send


class TraceIdMiddleware:
    """Attach a trace_id to every HTTP request.

    Pure ASGI implementation -- operates directly on scope/receive/send
    without intermediate abstractions.

    Non-HTTP scopes (lifespan, websocket) are passed through unchanged.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Extract trace_id from request headers or generate a new one.
        trace_id = _extract_trace_id(scope) or str(uuid4())

        # Bind to structlog contextvars -- every log call in this
        # request will include trace_id automatically via
        # merge_contextvars processor.
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(trace_id=trace_id)

        async def send_with_trace_id(message: dict) -> None:
            """Inject X-Trace-ID into response headers."""
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers.append("X-Trace-ID", trace_id)
            await send(message)

        await self.app(scope, receive, send_with_trace_id)


def _extract_trace_id(scope: Scope) -> str | None:
    """Read X-Trace-ID from ASGI scope headers.

    ASGI headers are list of (name, value) byte-tuples.
    Returns None if header is missing or empty.
    """
    for name, value in scope.get("headers", []):
        if name == b"x-trace-id":
            decoded = value.decode("latin-1")
            return decoded if decoded else None
    return None
