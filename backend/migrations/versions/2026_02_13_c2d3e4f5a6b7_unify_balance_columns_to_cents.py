"""unify_balance_columns_to_cents

Convert balance columns from Numeric(18,2) to Integer (cents).
Rename for consistency with amount_cents convention (TD-033).

  User.balance_user             → User.balance_cents
  MasterProfile.frozen_amount   → MasterProfile.frozen_cents
  MasterProfile.available_amount→ MasterProfile.available_cents

Safe: all values are currently 0 (payments not yet implemented).

Revision ID: c2d3e4f5a6b7
Revises: b1c2d3e4f5a6
Create Date: 2026-02-13
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c2d3e4f5a6b7"
down_revision: str | None = "b1c2d3e4f5a6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # -- users.balance_user → balance_cents (Numeric → Integer) --
    op.alter_column(
        "users",
        "balance_user",
        new_column_name="balance_cents",
        type_=sa.Integer(),
        server_default="0",
        existing_nullable=False,
        postgresql_using="balance_user::integer",
    )

    # -- master_profiles.frozen_amount → frozen_cents --
    op.alter_column(
        "master_profiles",
        "frozen_amount",
        new_column_name="frozen_cents",
        type_=sa.Integer(),
        server_default="0",
        existing_nullable=False,
        postgresql_using="frozen_amount::integer",
    )

    # -- master_profiles.available_amount → available_cents --
    op.alter_column(
        "master_profiles",
        "available_amount",
        new_column_name="available_cents",
        type_=sa.Integer(),
        server_default="0",
        existing_nullable=False,
        postgresql_using="available_amount::integer",
    )


def downgrade() -> None:
    # -- Revert available_cents → available_amount --
    op.alter_column(
        "master_profiles",
        "available_cents",
        new_column_name="available_amount",
        type_=sa.Numeric(precision=18, scale=2),
        server_default="0",
        existing_nullable=False,
        postgresql_using="available_cents::numeric(18,2)",
    )

    # -- Revert frozen_cents → frozen_amount --
    op.alter_column(
        "master_profiles",
        "frozen_cents",
        new_column_name="frozen_amount",
        type_=sa.Numeric(precision=18, scale=2),
        server_default="0",
        existing_nullable=False,
        postgresql_using="frozen_cents::numeric(18,2)",
    )

    # -- Revert balance_cents → balance_user --
    op.alter_column(
        "users",
        "balance_cents",
        new_column_name="balance_user",
        type_=sa.Numeric(precision=18, scale=2),
        server_default="0",
        existing_nullable=False,
        postgresql_using="balance_cents::numeric(18,2)",
    )
