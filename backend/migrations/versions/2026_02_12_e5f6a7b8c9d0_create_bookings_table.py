"""create_bookings_table

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-02-12
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e5f6a7b8c9d0"
down_revision: str | None = "d4e5f6a7b8c9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "bookings",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "practice_id",
            sa.UUID(),
            sa.ForeignKey("practices.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.UUID(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(20),
            server_default="pending",
            nullable=False,
        ),
        # Stub column -- no FK until Phase 6.4 (purchases).
        sa.Column(
            "purchase_id",
            sa.UUID(),
            nullable=True,
        ),
        sa.Column(
            "cancelled_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "cancellation_reason",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "joined_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "left_at",
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
        sa.UniqueConstraint(
            "practice_id",
            "user_id",
            name="uq_booking_practice_user",
        ),
    )
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


def downgrade() -> None:
    op.drop_index(
        "ix_bookings_user_id", table_name="bookings",
    )
    op.drop_index(
        "ix_bookings_practice_id", table_name="bookings",
    )
    op.drop_table("bookings")
