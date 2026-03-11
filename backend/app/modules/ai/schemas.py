# =============================================================================
# VELO Backend -- AI Schemas (Phase 9.1)
# =============================================================================
#
# Response models for GET /api/v1/practices/{id}/ai-summary.
# =============================================================================

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AISummaryResponse(BaseModel):
    """GET /api/v1/practices/{id}/ai-summary -- response body.

    practice_id: The practice this summary belongs to.
    summary:     Generated text. Placeholder in Phase 9.1.
    is_mock:     True when returned by MockAIService.
    generated_at: When the summary was produced.
    """

    practice_id: UUID
    summary: str
    is_mock: bool
    generated_at: datetime
