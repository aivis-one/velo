# =============================================================================
# Migration: Create feedbacks table (Phase 8.2)
# =============================================================================
# 1. CREATE TABLE feedbacks
# 2. Indexes for common queries (practice_id, user_id, booking_id)
# 3. Unique constraint: one feedback per (practice_id, user_id)
# =============================================================================

"""create_feedbacks_table

Revision ID: b9c2d3e4f5a6
Revises: a8b1c2d3e4f5
Create Date: 2026-02-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b9c2d3e4f5a6"
down_revision: str | None = "a8b1c2d3e4f5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create feedbacks table."""
    op.create_table(
        "feedbacks",
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
        sa.Column("rating", sa.String(10), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "practice_id",
            "user_id",
            name="uq_feedback_practice_user",
        ),
    )
    # Indexes for common queries.
    op.create_index(
        "ix_feedbacks_practice_id",
        "feedbacks",
        ["practice_id"],
    )
    op.create_index(
        "ix_feedbacks_user_id",
        "feedbacks",
        ["user_id"],
    )
    op.create_index(
        "ix_feedbacks_booking_id",
        "feedbacks",
        ["booking_id"],
    )


def downgrade() -> None:
    """Drop feedbacks table."""
    op.drop_table("feedbacks")
