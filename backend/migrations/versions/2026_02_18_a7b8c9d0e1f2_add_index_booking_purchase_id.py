"""Add index on bookings.purchase_id (W-02).

The FK constraint fk_bookings_purchase_id already exists in DB
(added in e4f5a6b7c8d9_create_purchases_table). This migration
adds a B-tree index for JOIN/lookup performance.

Revision ID: a7b8c9d0e1f2
Revises: f5a6b7c8d9e0
Create Date: 2026-02-18
"""

from collections.abc import Sequence

from alembic import op

revision: str = "a7b8c9d0e1f2"
down_revision: str | None = "f5a6b7c8d9e0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "ix_bookings_purchase_id",
        "bookings",
        ["purchase_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_bookings_purchase_id",
        table_name="bookings",
    )
