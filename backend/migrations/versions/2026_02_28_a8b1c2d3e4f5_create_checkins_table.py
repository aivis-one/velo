# =============================================================================
# Migration: Create checkins table (Phase 8.1)
# =============================================================================
# 1. CREATE TABLE checkins
# 2. Indexes for common queries (practice_id, user_id, booking_id)
# 3. Unique constraint: one check-in per (booking_id, check_type)
# =============================================================================

"""create_checkins_table

Revision ID: a8b1c2d3e4f5
Revises: 0a1b2c3d4e5f
Create Date: 2026-02-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a8b1c2d3e4f5"
down_revision: str | None = "0a1b2c3d4e5f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create checkins table."""
    op.create_table(
        "checkins",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "practice_id",
            sa.UUID(),
            sa.ForeignKey("practices.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.UUID(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "booking_id",
            sa.UUID(),
            sa.ForeignKey("bookings.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("mood", sa.String(10), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column(
            "check_type",
            sa.String(10),
            server_default="pre",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "booking_id",
            "check_type",
            name="uq_checkin_booking_type",
        ),
    )
    # Indexes for common queries.
    op.create_index(
        "ix_checkins_practice_id",
        "checkins",
        ["practice_id"],
    )
    op.create_index(
        "ix_checkins_user_id",
        "checkins",
        ["user_id"],
    )
    op.create_index(
        "ix_checkins_booking_id",
        "checkins",
        ["booking_id"],
    )


def downgrade() -> None:
    """Drop checkins table."""
    op.drop_table("checkins")
