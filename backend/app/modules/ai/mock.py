# =============================================================================
# VELO Backend -- AI Mock Service (Phase 9.1)
# =============================================================================
#
# Placeholder implementation of AIServiceProtocol.
# Returns a static summary text so the endpoint is functional
# without an external LLM dependency.
#
# Replace with a real implementation when the AI service is ready.
# The router depends on get_ai_service() from interface.py -- swap
# only that factory to go live.
# =============================================================================

from datetime import datetime, timezone
from uuid import UUID

from app.modules.ai.schemas import AISummaryResponse

_PLACEHOLDER_SUMMARY = (
    "AI-summary is not yet available. "
    "This feature will analyse participant check-ins, feedback, "
    "and session attendance to generate a personalised post-practice "
    "report for the master. Coming soon."
)


class MockAIService:
    """Stub AI service that returns a static placeholder.

    Satisfies AIServiceProtocol without any external calls.
    """

    async def generate_summary(
        self,
        practice_id: UUID,
    ) -> AISummaryResponse:
        """Return a placeholder summary for any practice."""
        return AISummaryResponse(
            practice_id=practice_id,
            summary=_PLACEHOLDER_SUMMARY,
            is_mock=True,
            generated_at=datetime.now(timezone.utc),
        )
