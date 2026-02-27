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
#
# SECURITY (SEC-01):
#   Client-provided trace_id is validated against a safe character set
#   (alphanumeric + dots, hyphens, underscores). This prevents log
#   injection, header injection, and JSONB pollution via crafted
#   X-Trace-ID values that end up in AuditLog.trace_id (String(36)).
# =============================================================================

import re
from uuid import uuid4

import structlog
from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Receive, Scope, Send

# SEC-01: Safe character set for client-provided trace IDs.
# Allows UUIDs (hex + hyphens), custom IDs like "my-custom-trace-42",
# and dotted formats like "svc.req.123". Rejects spaces, newlines,
# unicode, quotes, slashes, and other injection vectors.
_TRACE_ID_RE = re.compile(r"^[a-zA-Z0-9._-]+$")


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

        # Extract request context from ASGI scope headers.
        # Guard: AuditLog.trace_id is String(36). If client sends
        # a longer value, discard it and generate a fresh uuid4
        # to prevent DataError in financial transactions (Phase 6+).
        #
        # SEC-01: additionally validate character set to prevent
        # log injection and JSONB pollution via crafted trace IDs.
        raw_trace = _extract_header(scope, b"x-trace-id") or ""
        if (
            0 < len(raw_trace) <= 36
            and _TRACE_ID_RE.match(raw_trace)
        ):
            trace_id = raw_trace
        else:
            trace_id = str(uuid4())

        ip_address = _extract_client_ip(scope)
        user_agent = _extract_header(scope, b"user-agent")

        # Bind to structlog contextvars -- every log call in this
        # request will include trace_id automatically via
        # merge_contextvars processor. ip_address and user_agent
        # are consumed by record_audit() (Pre-6.2).
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            trace_id=trace_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        async def send_with_trace_id(message: dict) -> None:
            """Inject X-Trace-ID into response headers."""
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers.append("X-Trace-ID", trace_id)
            await send(message)

        await self.app(scope, receive, send_with_trace_id)


def _extract_header(scope: Scope, name: bytes) -> str | None:
    """Read a single header value from ASGI scope.

    ASGI headers are list of (name, value) byte-tuples.
    Returns None if header is missing or empty.
    """
    for header_name, header_value in scope.get("headers", []):
        if header_name == name:
            decoded = header_value.decode("latin-1")
            return decoded if decoded else None
    return None


def _extract_client_ip(scope: Scope) -> str | None:
    """Extract client IP address.

    Prefers X-Forwarded-For (set by Nginx reverse proxy),
    falls back to ASGI scope client address.
    """
    forwarded = _extract_header(scope, b"x-forwarded-for")
    if forwarded:
        # X-Forwarded-For can be "client, proxy1, proxy2".
        return forwarded.split(",")[0].strip()

    client = scope.get("client")
    if client:
        return client[0]

    return None
