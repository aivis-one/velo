# =============================================================================
# Test: Trace ID Middleware (Pre-6.1)
# =============================================================================
#
# Verifies that every HTTP response contains an X-Trace-ID header:
#   - Auto-generated uuid4 when client doesn't provide one
#   - Echoed back when client provides X-Trace-ID
#
# No auth or DB needed -- uses public GET / endpoint.
# =============================================================================

from uuid import UUID

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_trace_id_generated_when_missing(
    client: AsyncClient,
) -> None:
    """Response contains a valid uuid4 X-Trace-ID when not provided."""
    resp = await client.get("/")
    assert resp.status_code == 200

    trace_id = resp.headers.get("x-trace-id")
    assert trace_id is not None

    # Must be a valid UUID.
    UUID(trace_id)


@pytest.mark.asyncio
async def test_trace_id_passthrough(
    client: AsyncClient,
) -> None:
    """Client-provided X-Trace-ID is echoed back in response."""
    custom_id = "my-custom-trace-42"
    resp = await client.get(
        "/",
        headers={"X-Trace-ID": custom_id},
    )
    assert resp.status_code == 200
    assert resp.headers.get("x-trace-id") == custom_id


@pytest.mark.asyncio
async def test_trace_id_unique_per_request(
    client: AsyncClient,
) -> None:
    """Two requests without X-Trace-ID get different trace IDs."""
    resp1 = await client.get("/")
    resp2 = await client.get("/")

    trace1 = resp1.headers.get("x-trace-id")
    trace2 = resp2.headers.get("x-trace-id")

    assert trace1 is not None
    assert trace2 is not None
    assert trace1 != trace2
