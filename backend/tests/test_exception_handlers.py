# =============================================================================
# VELO Backend -- Exception Handler Tests (W4 fix)
# =============================================================================
#
# W4: both 5xx exception handlers logged message-only, no traceback --
# every real production 500 lost its stack trace. Fix adds exc_info=exc so
# structlog's format_exc_info processor renders the traceback.
#
# These call the handlers directly (unit-style) rather than through a live
# route, since neither handler needs the full ASGI stack to verify what it
# passes to the logger.
# =============================================================================

from unittest.mock import MagicMock, patch

import pytest
from starlette.requests import Request

from app.core.exceptions import VeloError
from app.main import global_exception_handler, velo_error_handler


def _fake_request(path: str = "/test") -> Request:
    return Request(
        scope={
            "type": "http",
            "path": path,
            "method": "GET",
            "headers": [],
        },
    )


@pytest.mark.asyncio
async def test_global_exception_handler_logs_exc_info() -> None:
    """Unhandled exceptions must log exc_info so the traceback isn't lost."""
    exc = ValueError("boom")

    with patch("app.main.logger") as mock_logger:
        response = await global_exception_handler(_fake_request(), exc)

    assert response.status_code == 500
    _, kwargs = mock_logger.error.call_args
    assert kwargs.get("exc_info") is exc


@pytest.mark.asyncio
async def test_velo_error_handler_logs_exc_info_on_5xx() -> None:
    """A >=500 VeloError must log exc_info so the traceback isn't lost."""
    exc = VeloError("db exploded", status_code=500, code="internal_error")

    with patch("app.main.logger") as mock_logger:
        response = await velo_error_handler(_fake_request(), exc)

    assert response.status_code == 500
    _, kwargs = mock_logger.error.call_args
    assert kwargs.get("exc_info") is exc


@pytest.mark.asyncio
async def test_velo_error_handler_does_not_log_exc_info_below_500() -> None:
    """A <500 VeloError logs a warning, not an error -- no exc_info needed."""
    exc = VeloError("not found", status_code=404, code="not_found")

    with patch("app.main.logger") as mock_logger:
        response = await velo_error_handler(_fake_request(), exc)

    assert response.status_code == 404
    mock_logger.error.assert_not_called()
    mock_logger.warning.assert_called_once()
