# =============================================================================
# VELO Backend -- Admin Users Schemas (Phase 3.2)
# =============================================================================

from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.users.schemas import UserResponse


class PaginatedParams(BaseModel):
    """Shared pagination query parameters."""

    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class PaginatedUsersResponse(BaseModel):
    """GET /api/v1/admin/users -- paginated user list."""

    items: list[UserResponse]
    total: int
    limit: int
    offset: int


class AdminMasterListItem(BaseModel):
    """Single item in admin masters list -- user data + master status."""

    id: UUID
    telegram_id: int | None = None
    first_name: str | None = None
    last_name: str | None = None
    avatar_url: str | None = None
    role: str
    is_active: bool
    master_status: str = Field(description="MasterProfile account status")


class PaginatedMastersResponse(BaseModel):
    """GET /api/v1/admin/masters -- paginated master list."""

    items: list[AdminMasterListItem]
    total: int
    limit: int
    offset: int
