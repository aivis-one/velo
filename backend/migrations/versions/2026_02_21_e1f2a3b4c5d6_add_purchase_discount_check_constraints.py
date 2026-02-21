# =============================================================================
# Migration: Add CHECK constraints for purchase discount invariants (Phase 6.7)
# =============================================================================
# BUG-15 fix: enforce discount_cents >= 0 and
# paid_cents = amount_cents - discount_cents at DB level.
# =============================================================================

"""add_purchase_discount_check_constraints

Revision ID: e1f2a3b4c5d6
Revises: d0e1f2a3b4c5
Create Date: 2026-02-21
"""

from collections.abc import Sequence

from alembic import op

revision: str = "e1f2a3b4c5d6"
down_revision: str | None = "d0e1f2a3b4c5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add CHECK constraints for purchase amount invariants."""
    op.create_check_constraint(
        "ck_purchases_discount_cents_non_negative",
        "purchases",
        "discount_cents >= 0",
    )
    op.create_check_constraint(
        "ck_purchases_paid_equals_amount_minus_discount",
        "purchases",
        "paid_cents = amount_cents - discount_cents",
    )


def downgrade() -> None:
    """Remove purchase amount CHECK constraints."""
    op.drop_constraint(
        "ck_purchases_paid_equals_amount_minus_discount",
        "purchases",
        type_="check",
    )
    op.drop_constraint(
        "ck_purchases_discount_cents_non_negative",
        "purchases",
        type_="check",
    )
