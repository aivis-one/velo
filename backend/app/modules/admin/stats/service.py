# =============================================================================
# VELO Backend -- Admin Stats Service (Phase 3.1, updated Phase 4.1)
# =============================================================================
#
# Platform statistics for admin dashboard.
#
# QUERIES (all read-only, no session mutations):
#   - users_count:          COUNT(*) from users
#   - masters_count:        COUNT(*) from users WHERE role = 'master'
#   - practices_count:      COUNT(*) from practices (Phase 4.1)
#   - pending_verifications: COUNT(*) from master_profiles
#                            WHERE data->'account'->>'status' = 'pending'
# =============================================================================

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.admin.stats.schemas import AdminStatsResponse
from app.modules.masters.models import MasterProfile
from app.modules.practices.models import Practice
from app.modules.users.models import User, UserRole

logger = structlog.get_logger()


async def get_stats(session: AsyncSession) -> AdminStatsResponse:
    """Compute platform-wide statistics.

    Runs four COUNT queries in the same session. Users and masters
    counts use indexed columns. Pending count does a sequential scan
    on master_profiles (small table, no GIN index needed for MVP).
    """
    # -- Total users --
    users_result = await session.execute(select(func.count(User.id)))
    users_count = users_result.scalar_one()

    # -- Verified masters (role = 'master') --
    masters_result = await session.execute(
        select(func.count(User.id)).where(User.role == UserRole.MASTER)
    )
    masters_count = masters_result.scalar_one()

    # -- Pending master applications (JSONB filter) --
    pending_result = await session.execute(
        select(func.count(MasterProfile.user_id)).where(
            MasterProfile.data["account"]["status"].as_string() == "pending"
        )
    )
    pending_verifications = pending_result.scalar_one()

    # -- Total practices --
    practices_result = await session.execute(select(func.count(Practice.id)))
    practices_count = practices_result.scalar_one()

    logger.info(
        "admin_stats_fetched",
        users=users_count,
        masters=masters_count,
        practices=practices_count,
        pending=pending_verifications,
    )

    return AdminStatsResponse(
        users_count=users_count,
        masters_count=masters_count,
        practices_count=practices_count,
        pending_verifications=pending_verifications,
    )
