# =============================================================================
# Migration: Add what_to_prepare and contraindications to practices (DS-sprint)
# =============================================================================
# Adds two nullable Text columns to the practices table:
#   what_to_prepare   -- items participants should bring / prepare
#   contraindications -- medical / safety contraindications
#
# Both columns are nullable -- existing rows default to NULL.
# No data migration needed.
# =============================================================================

"""add_what_to_prepare_contraindications_to_practices

Revision ID: a1b2c3d4e5f7
Revises: f3a4b5c6d7e8
Create Date: 2026-03-21
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f7"
down_revision: str | None = "f3a4b5c6d7e8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add what_to_prepare and contraindications columns to practices."""
    op.add_column(
        "practices",
        sa.Column("what_to_prepare", sa.Text(), nullable=True),
    )
    op.add_column(
        "practices",
        sa.Column("contraindications", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    """Remove what_to_prepare and contraindications columns from practices."""
    op.drop_column("practices", "contraindications")
    op.drop_column("practices", "what_to_prepare")
