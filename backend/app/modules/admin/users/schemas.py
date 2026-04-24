# =============================================================================
# VELO Backend -- Admin Users Schemas (Phase 3.2)
# =============================================================================

from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.users.models import UserRole
from app.modules.users.schemas import UserResponse


class PaginatedUsersResponse(BaseModel):
    """GET /api/v1/admin/users -- paginated user list."""

    items: list[UserResponse]
    total: int
    limit: int
    offset: int


class AdminMasterListItem(BaseModel):
    """Single item in admin masters list -- user data + master status.

    CR-01: role narrowed from str to UserRole for type safety.
    """

    id: UUID
    telegram_id: int | None = None
    first_name: str | None = None
    last_name: str | None = None
    avatar_url: str | None = None
    role: UserRole
    is_active: bool
    master_status: str = Field(description="MasterProfile account status")


class PaginatedMastersResponse(BaseModel):
    """GET /api/v1/admin/masters -- paginated master list."""

    items: list[AdminMasterListItem]
    total: int
    limit: int
    offset: int
