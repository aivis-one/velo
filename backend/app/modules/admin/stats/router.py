# =============================================================================
# VELO Backend -- Admin Stats Router (Phase 3.1)
# =============================================================================
#
# ENDPOINTS:
#   GET /api/v1/admin/stats -- platform statistics
#
# AUTH: get_current_admin.
# SESSION: read-only (get_db_reader) -- no mutations.
# =============================================================================

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_reader
from app.modules.admin.stats.schemas import AdminStatsResponse
from app.modules.admin.stats.service import get_stats
from app.modules.auth.dependencies import get_current_admin
from app.modules.users.models import User

router = APIRouter()


@router.get("/stats", response_model=AdminStatsResponse)
async def get_admin_stats(
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_reader),
) -> AdminStatsResponse:
    """Return platform-wide statistics for admin dashboard.

    Read-only endpoint. practices_count is a stub (0) until Phase 4.
    """
    return await get_stats(session)
