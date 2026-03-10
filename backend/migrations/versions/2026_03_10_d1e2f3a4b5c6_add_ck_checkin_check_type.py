# =============================================================================
# Migration: Add check constraint on checkins.check_type (11.3 fix)
# =============================================================================
# Adds ck_checkin_check_type to enforce check_type IN ('pre', 'post')
# at the DB level. mood and rating already had constraints (Phase 8.3
# migration). check_type was the only enum column in diary models without
# DB-level validation — non-API write paths could insert invalid values.
# =============================================================================

"""add_ck_checkin_check_type

Revision ID: d1e2f3a4b5c6
Revises: c0d1e2f3a4b5
Create Date: 2026-03-10
"""

from collections.abc import Sequence

from alembic import op

revision: str = "d1e2f3a4b5c6"
down_revision: str | None = "d2f3a4b5c6e7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add check_type constraint to checkins table."""
    op.create_check_constraint(
        "ck_checkin_check_type",
        "checkins",
        "check_type IN ('pre', 'post')",
    )


def downgrade() -> None:
    """Remove check_type constraint from checkins table."""
    op.drop_constraint(
        "ck_checkin_check_type",
        "checkins",
        type_="check",
    )
