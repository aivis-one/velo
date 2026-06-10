# =============================================================================
# Migration: Add checkin_skipped to bookings (B2)
# =============================================================================
# Adds a non-null boolean column `checkin_skipped` to the bookings table:
#   checkin_skipped -- the user persistently skipped their PRE check-in for this
#                      booking. Was client-only before; persisting it keeps the
#                      dashboard banner / check-in prompt hidden across sessions
#                      and devices.
#
# NOT NULL with server_default false -- existing rows backfill to false (no one
# has skipped yet). No data migration needed.
# =============================================================================

"""add_checkin_skipped_to_bookings

Revision ID: f7a8b9c0d1e2
Revises: e6f7a8b9c0d1
Create Date: 2026-06-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "f7a8b9c0d1e2"
down_revision: str | None = "e6f7a8b9c0d1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add checkin_skipped column to bookings (NOT NULL, default false)."""
    op.add_column(
        "bookings",
        sa.Column(
            "checkin_skipped",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )


def downgrade() -> None:
    """Remove checkin_skipped column from bookings."""
    op.drop_column("bookings", "checkin_skipped")
