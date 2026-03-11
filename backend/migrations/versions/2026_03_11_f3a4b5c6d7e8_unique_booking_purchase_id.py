# =============================================================================
# Migration: Add partial unique index on bookings.purchase_id (B-04)
# =============================================================================
#
# Enforces 1:1 Booking <-> Purchase at the DB level from the Booking side.
# Purchase.booking_id already has unique=True (the other side).
#
# WHY PARTIAL (WHERE purchase_id IS NOT NULL):
#   purchase_id is nullable. A booking is created before the purchase,
#   so purchase_id starts as NULL. PostgreSQL includes NULLs in plain
#   unique indexes, which would prevent more than one NULL (i.e., only
#   one booking could ever be purchase-less). The partial index excludes
#   NULLs -- only non-NULL values are subject to uniqueness.
#
# REPLACES ix_bookings_purchase_id:
#   The old plain B-tree index (added in a7b8c9d0e1f2) is dropped here.
#   The unique index covers the same lookup performance need, so no
#   separate non-unique index is required.
#
# SAFETY CHECK:
#   A DO block runs before the index creation. If any duplicate
#   purchase_id values exist (two bookings pointing to the same purchase),
#   the migration raises an exception and aborts cleanly without leaving
#   the schema in a partial state.
#
# =============================================================================

"""add_unique_booking_purchase_id

Revision ID: f3a4b5c6d7e8
Revises: e2f3a4b5c6d7
Create Date: 2026-03-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "f3a4b5c6d7e8"
down_revision: str | None = "e2f3a4b5c6d7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Replace plain index with partial unique index on bookings.purchase_id."""
    # Safety check: abort if duplicates exist.
    # Two bookings sharing the same purchase_id would violate the invariant
    # we are about to enforce. Fix data manually before re-running.
    op.execute(
        sa.text("""
            DO $$
            DECLARE
                dup_count INTEGER;
            BEGIN
                SELECT COUNT(*) INTO dup_count
                FROM (
                    SELECT purchase_id
                    FROM bookings
                    WHERE purchase_id IS NOT NULL
                    GROUP BY purchase_id
                    HAVING COUNT(*) > 1
                ) sub;

                IF dup_count > 0 THEN
                    RAISE EXCEPTION
                        'B-04 migration aborted: % duplicate purchase_id value(s) found in bookings. '
                        'Fix data manually before re-running.',
                        dup_count;
                END IF;
            END
            $$;
        """)
    )

    # Drop the old plain B-tree index (added in a7b8c9d0e1f2).
    # The new unique index covers the same lookup performance need.
    op.drop_index(
        "ix_bookings_purchase_id",
        table_name="bookings",
    )

    # Create partial unique index: NULLs excluded, non-NULLs must be unique.
    op.create_index(
        "uq_booking_purchase_id",
        "bookings",
        ["purchase_id"],
        unique=True,
        postgresql_where=sa.text("purchase_id IS NOT NULL"),
    )


def downgrade() -> None:
    """Revert to plain B-tree index on bookings.purchase_id."""
    op.drop_index(
        "uq_booking_purchase_id",
        table_name="bookings",
    )

    op.create_index(
        "ix_bookings_purchase_id",
        "bookings",
        ["purchase_id"],
    )
