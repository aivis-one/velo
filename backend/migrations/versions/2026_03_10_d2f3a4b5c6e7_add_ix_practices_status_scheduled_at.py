# =============================================================================
# Migration: Add composite index on practices(status, scheduled_at)
# =============================================================================
# WARNING-7 fix: list_public_practices query pattern:
#   WHERE status = ? AND scheduled_at >= ? ORDER BY scheduled_at
# Without this index, the query does a full table scan on practices.
# =============================================================================

"""add_ix_practices_status_scheduled_at

Revision ID: d2f3a4b5c6e7
Revises: c0d1e2f3a4b5
Create Date: 2026-03-10
"""

from collections.abc import Sequence

from alembic import op

revision: str = "d2f3a4b5c6e7"
down_revision: str | None = "c0d1e2f3a4b5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add composite index on practices(status, scheduled_at)."""
    op.create_index(
        "ix_practices_status_scheduled_at",
        "practices",
        ["status", "scheduled_at"],
    )


def downgrade() -> None:
    """Drop composite index on practices(status, scheduled_at)."""
    op.drop_index(
        "ix_practices_status_scheduled_at",
        table_name="practices",
    )
