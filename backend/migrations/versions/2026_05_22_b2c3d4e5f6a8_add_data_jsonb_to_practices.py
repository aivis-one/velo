# =============================================================================
# Migration: Add data JSONB sandbox to practices (Calendar iteration)
# =============================================================================
# Adds a single nullable-default JSONB column to the practices table:
#   data -- schema-on-read sandbox, mirroring master_profiles.data and
#           users.credentials. Holds Calendar taxonomy facets under
#           data.taxonomy: { direction, style, difficulty }.
#
# server_default '{}' (NOT NULL) -- existing rows get an empty object, so
# no data backfill is required. Taxonomy keys are populated lazily when a
# master creates / edits a practice (later batch).
# =============================================================================

"""add_data_jsonb_to_practices

Revision ID: b2c3d4e5f6a8
Revises: a1b2c3d4e5f7
Create Date: 2026-05-22
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "b2c3d4e5f6a8"
down_revision: str | None = "a1b2c3d4e5f7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add the data JSONB sandbox column to practices."""
    op.add_column(
        "practices",
        sa.Column(
            "data",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Remove the data JSONB sandbox column from practices."""
    op.drop_column("practices", "data")
