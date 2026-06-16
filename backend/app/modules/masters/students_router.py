# =============================================================================
# VELO Backend -- Master Students Router (E5)
# =============================================================================
#
# Master-facing "my students" CRM aggregate.
#
# ENDPOINTS:
#   GET /api/v1/masters/me/students        -- searchable, paginated list
#   GET /api/v1/masters/me/students/{id}   -- per-student detail aggregate
#
# Mounted as a SEPARATE router (like finance) so the dynamic /{user_id} route
# on the main masters router (single-segment) never shadows these two-segment
# /me/students* paths. The static /me/students is declared before the dynamic
# /me/students/{student_id}.
#
# AUTH: get_current_master on all endpoints (verified master only).
# SESSION: get_db_reader -- read-only.
# =============================================================================

from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_reader
from app.modules.auth.dependencies import get_current_master
from app.modules.masters.models import MasterProfile
from app.modules.masters.students_schemas import (
    PaginatedStudentsResponse,
    StudentDetailResponse,
    StudentListItem,
)
from app.modules.masters.students_service import (
    get_master_student_detail,
    list_master_students,
)
from app.modules.users.models import User

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/masters", tags=["master-students"])


@router.get("/me/students", response_model=PaginatedStudentsResponse)
async def list_my_students_endpoint(
    search: str | None = Query(default=None, min_length=1, max_length=100),
    master_tuple: tuple[User, MasterProfile] = Depends(get_current_master),
    session: AsyncSession = Depends(get_db_reader),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> PaginatedStudentsResponse:
    """List my students (users with >= 1 attended booking on my practices).

    Optional case-insensitive name search; most-attended first.
    """
    user, _profile = master_tuple
    items, total = await list_master_students(
        user.id, session, search=search, limit=limit, offset=offset,
    )
    return PaginatedStudentsResponse(
        items=[StudentListItem(**item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/me/students/{student_id}", response_model=StudentDetailResponse)
async def get_my_student_endpoint(
    student_id: UUID,
    master_tuple: tuple[User, MasterProfile] = Depends(get_current_master),
    session: AsyncSession = Depends(get_db_reader),
) -> StudentDetailResponse:
    """Per-student detail: counts, hours, satisfaction, recent activity.

    404 if the user is not this master's student (no attended booking).
    """
    user, _profile = master_tuple
    data = await get_master_student_detail(user.id, student_id, session)
    return StudentDetailResponse(**data)
