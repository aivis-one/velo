# =============================================================================
# VELO Backend -- AI Service Interface (Phase 9.1)
# =============================================================================
#
# Protocol definition for the AI summary service.
# The real implementation is out of MVP scope (Section 1.3).
# MockAIService is used until a real service is plugged in.
#
# USAGE:
#   Depend on AIServiceProtocol, not MockAIService directly.
#   When a real service is ready, swap the provider in router.py.
#
# SESSION RULES:
#   Session passed as read-only argument. Protocol does not commit.
# =============================================================================

from datetime import datetime, timezone
from typing import Protocol
from uuid import UUID

from app.modules.ai.schemas import AISummaryResponse


class AIServiceProtocol(Protocol):
    """Interface for the AI practice summary service.

    Any implementation must be callable as an async function.
    The real service will call an external LLM API.
    The mock returns a static placeholder.
    """

    async def generate_summary(
        self,
        practice_id: UUID,
    ) -> AISummaryResponse:
        """Generate a summary for a completed practice.

        Args:
            practice_id: UUID of the completed practice.

        Returns:
            AISummaryResponse with summary text and metadata.
        """
        ...


def get_ai_service() -> AIServiceProtocol:
    """FastAPI dependency -- returns the active AI service implementation.

    Phase 9.1: always returns MockAIService.
    Future: check settings.ai_provider and return the real client.
    """
    from app.modules.ai.mock import MockAIService  # noqa: PLC0415 -- lazy import
    return MockAIService()
