# =============================================================================
# Migration: Create promos table + add promo columns to purchases (Phase 6.7)
# =============================================================================
# 1. CREATE TABLE promos
# 2. ALTER TABLE purchases ADD amount_cents, discount_cents, promo_id
# 3. Data migration: amount_cents = paid_cents for existing rows
# =============================================================================

"""create_promos_and_update_purchases

Revision ID: d0e1f2a3b4c5
Revises: c9d0e1f2a3b4
Create Date: 2026-02-21
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d0e1f2a3b4c5"
down_revision: str | None = "c9d0e1f2a3b4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create promos table and add promo-related columns to purchases."""

    # -- 1. Create promos table --
    op.create_table(
        "promos",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("code", sa.String(50), nullable=False, unique=True),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column(
            "master_id",
            sa.UUID(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "practice_id",
            sa.UUID(),
            sa.ForeignKey("practices.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("discount_percent", sa.Integer(), nullable=False),
        sa.Column(
            "max_uses",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "used_count",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
        sa.Column(
            "valid_from",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "valid_until",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "first_purchase_only",
            sa.Boolean(),
            server_default="false",
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default="true",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_promos_master_id",
        "promos",
        ["master_id"],
    )
    op.create_index(
        "ix_promos_practice_id",
        "promos",
        ["practice_id"],
    )
    op.create_index(
        "ix_promos_is_active",
        "promos",
        ["is_active"],
    )
    # CHECK: discount_percent must be positive.
    op.create_check_constraint(
        "ck_promos_discount_percent_positive",
        "promos",
        "discount_percent > 0 AND discount_percent <= 100",
    )
    # CHECK: used_count non-negative.
    op.create_check_constraint(
        "ck_promos_used_count_non_negative",
        "promos",
        "used_count >= 0",
    )

    # -- 2. Add columns to purchases --
    op.add_column(
        "purchases",
        sa.Column(
            "amount_cents",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
    )
    op.add_column(
        "purchases",
        sa.Column(
            "discount_cents",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
    )
    op.add_column(
        "purchases",
        sa.Column(
            "promo_id",
            sa.UUID(),
            nullable=True,
        ),
    )
    op.create_foreign_key(
        "fk_purchases_promo_id",
        "purchases",
        "promos",
        ["promo_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_purchases_promo_id",
        "purchases",
        ["promo_id"],
    )

    # -- 3. Data migration: existing purchases have no promo --
    # amount_cents = paid_cents (full price = what was paid, no discount).
    op.execute(
        "UPDATE purchases SET amount_cents = paid_cents "
        "WHERE amount_cents = 0 AND paid_cents > 0"
    )


def downgrade() -> None:
    """Drop promo columns from purchases and drop promos table."""
    # -- Reverse purchases changes --
    op.drop_index("ix_purchases_promo_id", table_name="purchases")
    op.drop_constraint("fk_purchases_promo_id", "purchases", type_="foreignkey")
    op.drop_column("purchases", "promo_id")
    op.drop_column("purchases", "discount_cents")
    op.drop_column("purchases", "amount_cents")

    # -- Drop promos table --
    op.drop_constraint(
        "ck_promos_used_count_non_negative", "promos", type_="check",
    )
    op.drop_constraint(
        "ck_promos_discount_percent_positive", "promos", type_="check",
    )
    op.drop_index("ix_promos_is_active", table_name="promos")
    op.drop_index("ix_promos_practice_id", table_name="promos")
    op.drop_index("ix_promos_master_id", table_name="promos")
    op.drop_table("promos")
