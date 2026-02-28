# =============================================================================
# Migration: Create diary_entries table + add check constraints (Phase 8.3)
# =============================================================================
# 1. ADD CHECK CONSTRAINT on checkins.mood (WARNING-9 fix)
# 2. ADD CHECK CONSTRAINT on feedbacks.rating (WARNING-9 fix)
# 3. CREATE TABLE diary_entries
# 4. CHECK CONSTRAINT on diary_entries.mood
# 5. Indexes for common queries
# =============================================================================

"""create_diary_entries_table_and_check_constraints

Revision ID: c0d1e2f3a4b5
Revises: b9c2d3e4f5a6
Create Date: 2026-02-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c0d1e2f3a4b5"
down_revision: str | None = "b9c2d3e4f5a6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create diary_entries table and add check constraints."""
    # -- WARNING-9 fix: add check constraints to existing tables --
    op.create_check_constraint(
        "ck_checkin_mood",
        "checkins",
        "mood IN ('low', 'mid', 'high')",
    )
    op.create_check_constraint(
        "ck_feedback_rating",
        "feedbacks",
        "rating IN ('fire', 'good', 'confused')",
    )

    # -- Create diary_entries table --
    op.create_table(
        "diary_entries",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "user_id",
            sa.UUID(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "practice_id",
            sa.UUID(),
            sa.ForeignKey("practices.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("title", sa.String(200), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("mood", sa.String(10), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "mood IS NULL OR mood IN ('low', 'mid', 'high')",
            name="ck_diary_entry_mood",
        ),
    )
    # Indexes for common queries.
    op.create_index(
        "ix_diary_entries_user_id",
        "diary_entries",
        ["user_id"],
    )
    op.create_index(
        "ix_diary_entries_practice_id",
        "diary_entries",
        ["practice_id"],
    )


def downgrade() -> None:
    """Drop diary_entries table and check constraints."""
    op.drop_table("diary_entries")

    op.drop_constraint(
        "ck_feedback_rating",
        "feedbacks",
        type_="check",
    )
    op.drop_constraint(
        "ck_checkin_mood",
        "checkins",
        type_="check",
    )
