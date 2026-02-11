# =============================================================================
# VELO Backend -- Admin Router (Phase 3.1, updated Phase 3.2, Phase 3.3)
# =============================================================================
#
# Main router for all admin endpoints. Includes sub-routers:
#   - masters/  -- verify/reject master applications (Phase 2.3)
#   - stats/    -- platform statistics (Phase 3.1)
#   - users/    -- user and master listings (Phase 3.2)
#   - reports/  -- report management (Phase 3.3)
#
# All sub-routers inherit the /api/v1/admin prefix and "admin" tag.
# Auth: get_current_admin dependency is applied per-endpoint in
# each sub-router, not globally here.
# =============================================================================

from fastapi import APIRouter

from app.modules.admin.masters.router import router as masters_router
from app.modules.admin.reports.router import router as reports_router
from app.modules.admin.stats.router import router as stats_router
from app.modules.admin.users.router import router as users_router

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

router.include_router(masters_router)
router.include_router(stats_router)
router.include_router(users_router)
router.include_router(reports_router)
