# =============================================================================
# Migration: Add CHECK constraints and admin_id index to withdrawals
# =============================================================================
# BUG-03: amount_cents > 0, fee_cents >= 0
# BUG-05: index on admin_id FK (R-07 pattern)
# =============================================================================

"""add_withdrawals_checks_and_admin_idx

Revision ID: c9d0e1f2a3b4
Revises: b8c9d0e1f2a3
Create Date: 2026-02-20
"""

from alembic import op

revision = "c9d0e1f2a3b4"
down_revision = "b8c9d0e1f2a3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_withdrawals_amount_positive",
        "withdrawals",
        "amount_cents > 0",
    )
    op.create_check_constraint(
        "ck_withdrawals_fee_non_negative",
        "withdrawals",
        "fee_cents >= 0",
    )
    op.create_index(
        "ix_withdrawals_admin_id",
        "withdrawals",
        ["admin_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_withdrawals_admin_id", table_name="withdrawals")
    op.drop_constraint(
        "ck_withdrawals_fee_non_negative", "withdrawals",
    )
    op.drop_constraint(
        "ck_withdrawals_amount_positive", "withdrawals",
    )
