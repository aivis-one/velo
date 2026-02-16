"""create_purchases_table

Revision ID: e4f5a6b7c8d9
Revises: d3e4f5a6b7c8
Create Date: 2026-02-13
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e4f5a6b7c8d9"
down_revision: str | None = "d3e4f5a6b7c8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create purchases table and add FK on bookings.purchase_id."""
    # -- Create purchases table --
    op.create_table(
        "purchases",
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
            sa.ForeignKey("practices.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "booking_id",
            sa.UUID(),
            sa.ForeignKey("bookings.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "paid_cents",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
        sa.Column(
            "currency",
            sa.String(3),
            server_default="eur",
            nullable=False,
        ),
        sa.Column(
            "commission_cents",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(20),
            server_default="pending",
            nullable=False,
        ),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=True,
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
        "ix_purchases_user_id",
        "purchases",
        ["user_id"],
    )
    op.create_index(
        "ix_purchases_practice_id",
        "purchases",
        ["practice_id"],
    )
    op.create_index(
        "ix_purchases_status",
        "purchases",
        ["status"],
    )

    # -- Add FK on bookings.purchase_id (column exists, FK does not) --
    op.create_foreign_key(
        "fk_bookings_purchase_id",
        "bookings",
        "purchases",
        ["purchase_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    """Drop FK and purchases table."""
    op.drop_constraint(
        "fk_bookings_purchase_id",
        "bookings",
        type_="foreignkey",
    )
    op.drop_index("ix_purchases_status", table_name="purchases")
    op.drop_index("ix_purchases_practice_id", table_name="purchases")
    op.drop_index("ix_purchases_user_id", table_name="purchases")
    op.drop_table("purchases")
