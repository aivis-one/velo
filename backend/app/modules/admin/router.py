# =============================================================================
# VELO Backend -- Admin Router (Phase 3.1)
# =============================================================================
#
# Main router for all admin endpoints. Includes sub-routers:
#   - masters/  -- verify/reject master applications (Phase 2.3)
#   - stats/    -- platform statistics (Phase 3.1)
#   - (future)  -- users/, reports/ (Phase 3.2, 3.3)
#
# All sub-routers inherit the /api/v1/admin prefix and "admin" tag.
# Auth: get_current_admin dependency is applied per-endpoint in
# each sub-router, not globally here.
# =============================================================================

from fastapi import APIRouter

from app.modules.admin.masters.router import router as masters_router
from app.modules.admin.stats.router import router as stats_router

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

router.include_router(masters_router)
router.include_router(stats_router)
