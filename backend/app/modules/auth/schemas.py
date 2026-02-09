# =============================================================================
# VELO Backend — Auth Schemas
# =============================================================================
#
# Pydantic models for auth request/response validation.
# FastAPI auto-generates OpenAPI docs from these.
#
# NOTE: UserResponse lives in users/schemas.py (moved in Phase 1.4).
# Imported here for AuthResponse backward compatibility.
# =============================================================================

from pydantic import BaseModel, Field

from app.modules.users.schemas import UserResponse


class TelegramAuthRequest(BaseModel):
    """POST /api/v1/auth/telegram — request body."""

    init_data: str = Field(
        ...,
        description="Raw initData string from Telegram WebApp",
        min_length=1,
    )


class AuthResponse(BaseModel):
    """POST /api/v1/auth/telegram — response body."""

    user: UserResponse
    session_token: str
