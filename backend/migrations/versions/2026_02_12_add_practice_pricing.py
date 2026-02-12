"""add pricing columns to practices

Revision ID: c3d4e5f6a7b8
Revises: a1b2c3d4e5f6
Create Date: 2026-02-12
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c3d4e5f6a7b8"
down_revision: str | None = "a1b2c3d4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "practices",
        sa.Column(
            "is_free",
            sa.Boolean(),
            server_default="true",
            nullable=False,
        ),
    )
    op.add_column(
        "practices",
        sa.Column(
            "price_cents",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
    )
    op.add_column(
        "practices",
        sa.Column(
            "currency",
            sa.String(3),
            server_default="EUR",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("practices", "currency")
    op.drop_column("practices", "price_cents")
    op.drop_column("practices", "is_free")
