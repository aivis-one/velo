"""create_waitlist_table

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-02-12
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "f6a7b8c9d0e1"
down_revision: str | None = "e5f6a7b8c9d0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "waitlist",
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
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.String(20),
            server_default="waiting",
            nullable=False,
        ),
        sa.Column(
            "joined_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "notified_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "expires_at",
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
            name="uq_waitlist_practice_user",
        ),
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
    # Composite index for process_waitlist query:
    # WHERE practice_id = X AND status = 'waiting' ORDER BY position
    op.create_index(
        "ix_waitlist_practice_status_position",
        "waitlist",
        ["practice_id", "status", "position"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_waitlist_practice_status_position",
        table_name="waitlist",
    )
    op.drop_index(
        "ix_waitlist_user_id", table_name="waitlist",
    )
    op.drop_index(
        "ix_waitlist_practice_id", table_name="waitlist",
    )
    op.drop_table("waitlist")
