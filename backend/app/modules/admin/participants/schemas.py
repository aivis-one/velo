# =============================================================================
# VELO Backend -- Admin Participants Schemas (E1)
# =============================================================================
#
# Global participants list for the admin dashboard «Участников» card.
#
# AdminParticipant:                one row in GET /admin/participants.
# PaginatedParticipantsResponse:   paginated list (mirrors /admin/users).
#
# Times are raw (created_at + last_login_at); the frontend formats the
# «joined» / «last-active» labels, matching the admin/practices convention.
# practices_count = distinct non-cancelled bookings for the user.
# =============================================================================

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AdminParticipant(BaseModel):
    """One participant (platform user) in the global admin list."""

    id: UUID
    name: str
    telegram_id: int | None = None
    avatar_url: str | None = None
    practices_count: int
    created_at: datetime
    last_login_at: datetime | None = None


class PaginatedParticipantsResponse(BaseModel):
    """GET /api/v1/admin/participants -- paginated participant list."""

    items: list[AdminParticipant]
    total: int
    limit: int
    offset: int
