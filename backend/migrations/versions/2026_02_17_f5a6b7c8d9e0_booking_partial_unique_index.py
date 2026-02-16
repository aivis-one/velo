"""H-02: booking partial unique index for re-booking after cancel

Drop absolute UniqueConstraint(practice_id, user_id) which blocks
re-booking after cancellation. Replace with partial unique index
WHERE status != 'cancelled', allowing cancelled rows to coexist
with new active bookings for the same (practice_id, user_id) pair.

Revision ID: f5a6b7c8d9e0
Revises: e4f5a6b7c8d9
Create Date: 2026-02-17
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "f5a6b7c8d9e0"
down_revision: str | None = "e4f5a6b7c8d9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Replace absolute unique constraint with partial unique index."""
    # Step 1: Drop old absolute unique constraint.
    op.drop_constraint(
        "uq_booking_practice_user",
        "bookings",
        type_="unique",
    )

    # Step 2: Create partial unique index (PostgreSQL-specific).
    # Allows multiple cancelled rows for same (practice_id, user_id),
    # but only one non-cancelled row.
    op.create_index(
        "uq_booking_practice_user_active",
        "bookings",
        ["practice_id", "user_id"],
        unique=True,
        postgresql_where=sa.text("status != 'cancelled'"),
    )


def downgrade() -> None:
    """Revert to absolute unique constraint.

    WARNING: Will fail if duplicate (practice_id, user_id) rows exist
    from re-bookings after cancel. Manual cleanup required first.
    """
    op.drop_index(
        "uq_booking_practice_user_active",
        table_name="bookings",
    )
    op.create_unique_constraint(
        "uq_booking_practice_user",
        "bookings",
        ["practice_id", "user_id"],
    )
