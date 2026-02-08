# =============================================================================
# VELO Backend — Auth Schemas
# =============================================================================
#
# Pydantic models for auth request/response validation.
# FastAPI auto-generates OpenAPI docs from these.
# =============================================================================

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.users.models import UserRole


class TelegramAuthRequest(BaseModel):
    """POST /api/v1/auth/telegram — request body."""

    init_data: str = Field(
        ...,
        description="Raw initData string from Telegram WebApp",
        min_length=1,
    )


class UserResponse(BaseModel):
    """User data in auth response."""

    id: UUID
    telegram_id: int | None
    role: UserRole
    first_name: str | None
    last_name: str | None
    avatar_url: str | None
    timezone: str
    language: str
    is_active: bool
    balance_user: Decimal
    created_at: datetime
    last_login_at: datetime | None

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    """POST /api/v1/auth/telegram — response body."""

    user: UserResponse
    session_token: str
