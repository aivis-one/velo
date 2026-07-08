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


class AdminMasterDetail(AdminMasterListItem):
    """GET /api/v1/admin/masters/{id} -- single master with profile detail (T3).

    Extends the list item with the profile fields the admin review screen shows:
    ``methods`` (editable via PATCH /admin/masters/{id}/methods), plus
    ``experience_years`` and ``bio`` (display-only). All read from
    MasterProfile.data.profile (additive, no migration).
    """

    methods: list[str] = Field(default_factory=list)
    experience_years: int = 0
    bio: str | None = None


class PaginatedMastersResponse(BaseModel):
    """GET /api/v1/admin/masters -- paginated master list."""

    items: list[AdminMasterListItem]
    total: int
    limit: int
    offset: int
