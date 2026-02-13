"""create_ledger_tables

Revision ID: b1c2d3e4f5a6
Revises: a0b1c2d3e4f5
Create Date: 2026-02-13
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b1c2d3e4f5a6"
down_revision: str | None = "a0b1c2d3e4f5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # -- user_ledger --
    op.create_table(
        "user_ledger",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "user_id",
            sa.UUID(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("amount_cents", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.String(20),
            server_default="done",
            nullable=False,
        ),
        sa.Column("reason", sa.String(200), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_user_ledger_user_id",
        "user_ledger",
        ["user_id"],
    )
    op.create_index(
        "ix_user_ledger_created_at",
        "user_ledger",
        ["created_at"],
    )

    # -- master_ledger --
    op.create_table(
        "master_ledger",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "user_id",
            sa.UUID(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("amount_cents", sa.Integer(), nullable=False),
        sa.Column(
            "is_frozen",
            sa.Boolean(),
            server_default="true",
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(20),
            server_default="done",
            nullable=False,
        ),
        sa.Column("reason", sa.String(200), nullable=False),
        sa.Column(
            "practice_id",
            sa.UUID(),
            sa.ForeignKey("practices.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_master_ledger_user_id",
        "master_ledger",
        ["user_id"],
    )
    op.create_index(
        "ix_master_ledger_practice_id",
        "master_ledger",
        ["practice_id"],
    )
    op.create_index(
        "ix_master_ledger_created_at",
        "master_ledger",
        ["created_at"],
    )

    # -- company_ledger --
    op.create_table(
        "company_ledger",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("amount_cents", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column(
            "status",
            sa.String(20),
            server_default="done",
            nullable=False,
        ),
        sa.Column("reason", sa.String(200), nullable=False),
        sa.Column("reference_id", sa.UUID(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_company_ledger_reference_id",
        "company_ledger",
        ["reference_id"],
    )
    op.create_index(
        "ix_company_ledger_created_at",
        "company_ledger",
        ["created_at"],
    )


def downgrade() -> None:
    # -- company_ledger --
    op.drop_index(
        "ix_company_ledger_created_at",
        table_name="company_ledger",
    )
    op.drop_index(
        "ix_company_ledger_reference_id",
        table_name="company_ledger",
    )
    op.drop_table("company_ledger")

    # -- master_ledger --
    op.drop_index(
        "ix_master_ledger_created_at",
        table_name="master_ledger",
    )
    op.drop_index(
        "ix_master_ledger_practice_id",
        table_name="master_ledger",
    )
    op.drop_index(
        "ix_master_ledger_user_id",
        table_name="master_ledger",
    )
    op.drop_table("master_ledger")

    # -- user_ledger --
    op.drop_index(
        "ix_user_ledger_created_at",
        table_name="user_ledger",
    )
    op.drop_index(
        "ix_user_ledger_user_id",
        table_name="user_ledger",
    )
    op.drop_table("user_ledger")
