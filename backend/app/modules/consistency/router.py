# =============================================================================
# VELO Backend -- Admin Consistency Router (Phase 6.8)
# =============================================================================
#
# ENDPOINTS:
#   GET /api/v1/admin/consistency -- run all data consistency semaphores
#
# AUTH: get_current_admin.
# SESSION: get_db_reader -- all read-only (no mutations).
# =============================================================================

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_reader
from app.modules.admin.consistency.schemas import ConsistencyResponse
from app.modules.admin.consistency.service import run_all_semaphores
from app.modules.auth.dependencies import get_current_admin
from app.modules.users.models import User

router = APIRouter()


@router.get("/consistency", response_model=ConsistencyResponse)
async def get_consistency(
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_reader),
) -> ConsistencyResponse:
    """Run all data consistency semaphores and return results.

    21 checks across 5 categories: COUNT=COUNT, SUM=0,
    COMPUTED=ACTUAL, ORPHAN DETECTION, BUSINESS INVARIANTS.
    """
    return await run_all_semaphores(session)
