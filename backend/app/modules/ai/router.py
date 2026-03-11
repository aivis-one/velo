# =============================================================================
# VELO Backend -- AI Summary Router (Phase 9.1)
# =============================================================================
#
# ENDPOINTS:
#   GET /api/v1/practices/{id}/ai-summary -- mock AI summary for a practice
#
# AUTH: get_current_user. Practice must exist; non-owner gets 404 (P-08).
# SESSION: get_db_reader -- read-only.
#
# NOTE: Phase 9.1 is a stub ("розетка"). The endpoint always returns a
#   static placeholder from MockAIService. When a real AI service is ready,
#   only get_ai_service() in interface.py needs to change.
# =============================================================================

from uuid import UUID

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_reader
from app.core.exceptions import NotFoundError
from app.modules.ai.interface import AIServiceProtocol, get_ai_service
from app.modules.ai.schemas import AISummaryResponse
from app.modules.auth.dependencies import get_current_user
from app.modules.practices.models import Practice
from app.modules.users.models import User

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/practices", tags=["ai"])


@router.get(
    "/{practice_id}/ai-summary",
    response_model=AISummaryResponse,
)
async def get_ai_summary(
    practice_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_reader),
    ai_service: AIServiceProtocol = Depends(get_ai_service),
) -> AISummaryResponse:
    """Return an AI-generated summary for a practice.

    Phase 9.1: always returns a static placeholder (is_mock=True).
    Only the practice owner (master) can request a summary.
    Non-owners receive 404 to avoid revealing resource existence (P-08).
    """
    stmt = select(Practice).where(Practice.id == practice_id)
    result = await session.execute(stmt)
    practice = result.scalar_one_or_none()

    if practice is None or practice.master_id != user.id:
        raise NotFoundError("Practice not found")

    summary = await ai_service.generate_summary(practice_id)

    logger.info(
        "ai_summary_requested",
        practice_id=str(practice_id),
        master_id=str(user.id),
        is_mock=summary.is_mock,
    )

    return summary
