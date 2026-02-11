"""create_practices_table

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-02-12 18:00:00.000000+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c3d4e5f6a7b8"
down_revision: str | None = "b2c3d4e5f6a7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Apply this migration."""
    op.create_table(
        "practices",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "master_id",
            sa.UUID(),
            sa.ForeignKey("master_profiles.user_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("practice_type", sa.String(length=20), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default="draft",
            nullable=False,
        ),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "scheduled_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("timezone", sa.String(length=50), nullable=False),
        sa.Column("max_participants", sa.Integer(), nullable=True),
        sa.Column(
            "current_participants",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
        sa.Column("zoom_link", sa.String(length=500), nullable=True),
        sa.Column(
            "parent_practice_id",
            sa.UUID(),
            sa.ForeignKey("practices.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    # Index for listing practices by master.
    op.create_index(
        "ix_practices_master_id",
        "practices",
        ["master_id"],
    )
    # Index for listing practices by scheduled_at (public feed).
    op.create_index(
        "ix_practices_scheduled_at",
        "practices",
        ["scheduled_at"],
    )


def downgrade() -> None:
    """Revert this migration."""
    op.drop_index("ix_practices_scheduled_at", table_name="practices")
    op.drop_index("ix_practices_master_id", table_name="practices")
    op.drop_table("practices")
