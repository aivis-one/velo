# =============================================================================
# Migration: Add title + counterparty_id to master_ledger (E2)
# =============================================================================
# Adds two nullable columns to master_ledger for the master-facing transaction
# feed and income projection:
#   title           -- human-readable label; only rows the master should see as
#                      a transaction (sale / commission / refund) carry it.
#                      Internal plumbing rows leave it NULL and are filtered out.
#   counterparty_id -- the other party to the movement (the paying student for a
#                      sale/refund); NULL for platform-side rows (commission).
#                      FK users ON DELETE SET NULL -- the amount survives even if
#                      the counterparty user is later removed.
#
# Both nullable -- existing rows backfill to NULL (untitled => excluded from the
# feed and income sum, which is the correct historical behaviour). No data
# migration needed.
# =============================================================================

"""ledger_tx_fields

Revision ID: 9f1e2d3c4b5a
Revises: f7a8b9c0d1e2
Create Date: 2026-06-15
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "9f1e2d3c4b5a"
down_revision: str | None = "f7a8b9c0d1e2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add title + counterparty_id columns to master_ledger."""
    op.add_column(
        "master_ledger",
        sa.Column("title", sa.String(200), nullable=True),
    )
    op.add_column(
        "master_ledger",
        sa.Column("counterparty_id", sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        "fk_master_ledger_counterparty_id_users",
        "master_ledger",
        "users",
        ["counterparty_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_master_ledger_counterparty_id",
        "master_ledger",
        ["counterparty_id"],
    )


def downgrade() -> None:
    """Remove title + counterparty_id columns from master_ledger."""
    op.drop_index(
        "ix_master_ledger_counterparty_id",
        table_name="master_ledger",
    )
    op.drop_constraint(
        "fk_master_ledger_counterparty_id_users",
        "master_ledger",
        type_="foreignkey",
    )
    op.drop_column("master_ledger", "counterparty_id")
    op.drop_column("master_ledger", "title")
