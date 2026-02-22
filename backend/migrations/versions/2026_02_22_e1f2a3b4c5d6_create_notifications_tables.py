# =============================================================================
# Migration: Create notifications + notification_deliveries (Phase 7.1)
# =============================================================================
# 1. CREATE TABLE notifications
# 2. CREATE TABLE notification_deliveries
# 3. Indexes for processor queries (status + scheduled_at, priority)
# =============================================================================

"""create_notifications_tables

Revision ID: e1f2a3b4c5d6
Revises: d0e1f2a3b4c5
Create Date: 2026-02-22
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "e1f2a3b4c5d6"
down_revision: str | None = "d0e1f2a3b4c5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create notifications and notification_deliveries tables."""

    # -- 1. notifications --
    op.create_table(
        "notifications",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("target_type", sa.String(20), nullable=False),
        sa.Column("target_value", sa.String(200), nullable=False),
        sa.Column(
            "action_data",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "priority",
            sa.Integer(),
            server_default="5",
            nullable=False,
        ),
        sa.Column(
            "scheduled_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "expiry_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.String(20),
            server_default="pending",
            nullable=False,
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
    )
    # Single-column indexes for filtering.
    op.create_index(
        "ix_notifications_type",
        "notifications",
        ["type"],
    )
    op.create_index(
        "ix_notifications_status",
        "notifications",
        ["status"],
    )
    # Composite index for processor polling query:
    # WHERE status = 'pending' AND scheduled_at <= now()
    # ORDER BY priority ASC, scheduled_at ASC
    op.create_index(
        "ix_notifications_processor_poll",
        "notifications",
        ["status", "scheduled_at", "priority"],
    )

    # -- 2. notification_deliveries --
    op.create_table(
        "notification_deliveries",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "notification_id",
            sa.UUID(),
            sa.ForeignKey("notifications.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.UUID(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("channel", sa.String(20), nullable=False),
        sa.Column(
            "channel_options",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.String(20),
            server_default="pending",
            nullable=False,
        ),
        sa.Column(
            "sent_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "attempts",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
        sa.Column(
            "error_message",
            sa.Text(),
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
    )
    op.create_index(
        "ix_notification_deliveries_notification_id",
        "notification_deliveries",
        ["notification_id"],
    )
    op.create_index(
        "ix_notification_deliveries_user_id",
        "notification_deliveries",
        ["user_id"],
    )
    # Composite index for delivery processor:
    # WHERE status = 'pending' ORDER BY created_at
    op.create_index(
        "ix_notification_deliveries_status",
        "notification_deliveries",
        ["status"],
    )
    # CHECK: attempts non-negative.
    op.create_check_constraint(
        "ck_notification_deliveries_attempts_non_negative",
        "notification_deliveries",
        "attempts >= 0",
    )


def downgrade() -> None:
    """Drop notification_deliveries and notifications tables."""
    # Deliveries first (FK dependency).
    op.drop_constraint(
        "ck_notification_deliveries_attempts_non_negative",
        "notification_deliveries",
        type_="check",
    )
    op.drop_index(
        "ix_notification_deliveries_status",
        table_name="notification_deliveries",
    )
    op.drop_index(
        "ix_notification_deliveries_user_id",
        table_name="notification_deliveries",
    )
    op.drop_index(
        "ix_notification_deliveries_notification_id",
        table_name="notification_deliveries",
    )
    op.drop_table("notification_deliveries")

    # Notifications.
    op.drop_index(
        "ix_notifications_processor_poll",
        table_name="notifications",
    )
    op.drop_index(
        "ix_notifications_status",
        table_name="notifications",
    )
    op.drop_index(
        "ix_notifications_type",
        table_name="notifications",
    )
    op.drop_table("notifications")
