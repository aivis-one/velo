"""R-07: add indexes on frequently filtered FK columns

bookings.practice_id -- COUNT for capacity check on every booking.
bookings.user_id     -- future GET /bookings/me.
waitlist.practice_id -- process_waitlist on every cancellation.
waitlist.user_id     -- future GET /waitlist/me.

practices.master_id already has ix_practices_master_id (Phase 4.1
migration), only model synced (no DB change needed).

Revision ID: a1b2c3d4e5f6
Revises: f5a6b7c8d9e0
Create Date: 2026-02-18
"""

from collections.abc import Sequence

from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "f5a6b7c8d9e0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create B-tree indexes on FK columns used in frequent queries."""
    op.create_index(
        "ix_bookings_practice_id",
        "bookings",
        ["practice_id"],
    )
    op.create_index(
        "ix_bookings_user_id",
        "bookings",
        ["user_id"],
    )
    op.create_index(
        "ix_waitlist_practice_id",
        "waitlist",
        ["practice_id"],
    )
    op.create_index(
        "ix_waitlist_user_id",
        "waitlist",
        ["user_id"],
    )


def downgrade() -> None:
    """Drop FK indexes."""
    op.drop_index("ix_waitlist_user_id", table_name="waitlist")
    op.drop_index("ix_waitlist_practice_id", table_name="waitlist")
    op.drop_index("ix_bookings_user_id", table_name="bookings")
    op.drop_index("ix_bookings_practice_id", table_name="bookings")
