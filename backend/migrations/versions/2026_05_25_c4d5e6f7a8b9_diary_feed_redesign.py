# =============================================================================
# Migration: Diary feed redesign -- entry_type/practice_phase/soft-delete on
#            diary_entries + create diary_events journal (Diary redesign)
# =============================================================================
# 1. ALTER diary_entries:
#      + entry_type     (note/dream, default note)
#      + practice_phase (before/after, nullable)
#      + is_deleted     (soft delete, default false) + index
#      + check constraints for entry_type and practice_phase
# 2. CREATE TABLE diary_events (append-only timeline journal)
#      + check constraints (kind, source_type)
#      + composite index (user_id, occurred_at) -- feed query
#      + composite index (source_type, source_id) -- per-object upsert
#
# DiaryRelation / DiaryRelationItem are intentionally NOT created here -- the
# relations socket is designed (DiaryEvent.id is the single FK target) but
# deferred to a future iteration.
# =============================================================================

"""diary_feed_redesign

Revision ID: c4d5e6f7a8b9
Revises: b2c3d4e5f6a8
Create Date: 2026-05-25
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "c4d5e6f7a8b9"
down_revision: str | None = "b2c3d4e5f6a8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Apply the diary feed redesign schema changes."""
    # -- 1. ALTER diary_entries -----------------------------------------
    # entry_type: note (default) / dream. server_default keeps existing rows
    # valid (all become note). The DB is wiped each deploy, but the default
    # is correct regardless.
    op.add_column(
        "diary_entries",
        sa.Column(
            "entry_type",
            sa.String(length=10),
            server_default="note",
            nullable=False,
        ),
    )
    # practice_phase: before / after, nullable (only meaningful when linked).
    op.add_column(
        "diary_entries",
        sa.Column(
            "practice_phase",
            sa.String(length=10),
            nullable=True,
        ),
    )
    # is_deleted: soft delete flag, default false.
    op.add_column(
        "diary_entries",
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            server_default="false",
            nullable=False,
        ),
    )
    op.create_check_constraint(
        "ck_diary_entry_type",
        "diary_entries",
        "entry_type IN ('note', 'dream')",
    )
    op.create_check_constraint(
        "ck_diary_entry_phase",
        "diary_entries",
        "practice_phase IS NULL OR practice_phase IN ('before', 'after')",
    )
    # Index for the soft-delete filter on the legacy entry list.
    op.create_index(
        "ix_diary_entries_is_deleted",
        "diary_entries",
        ["is_deleted"],
    )

    # -- 2. CREATE diary_events -----------------------------------------
    op.create_table(
        "diary_events",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "user_id",
            sa.UUID(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(length=40), nullable=False),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column("source_type", sa.String(length=20), nullable=False),
        sa.Column("source_id", sa.UUID(), nullable=False),
        sa.Column(
            "snapshot",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
        sa.Column("text_search", sa.Text(), nullable=True),
        sa.Column(
            "is_hidden",
            sa.Boolean(),
            server_default="false",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "kind IN ("
            "'booking_confirmed', 'booking_cancelled_by_user', "
            "'practice_rescheduled', 'practice_cancelled_by_master', "
            "'practice_outcome', 'checkin', 'feedback', 'note', 'dream')",
            name="ck_diary_event_kind",
        ),
        sa.CheckConstraint(
            "source_type IN ("
            "'booking', 'practice', 'checkin', 'feedback', 'diary_entry')",
            name="ck_diary_event_source_type",
        ),
    )
    # Single-column index on user_id (CASCADE delete + point lookups). Matches
    # the model's index=True on user_id; the composite below does not cover
    # single-column user_id scans for the FK.
    op.create_index(
        "ix_diary_events_user_id",
        "diary_events",
        ["user_id"],
    )
    # Primary feed query: WHERE user_id=? [...] ORDER BY occurred_at DESC.
    op.create_index(
        "ix_diary_events_user_occurred",
        "diary_events",
        ["user_id", "occurred_at"],
    )
    # Per-object upsert/lookup: find the event for a given source object.
    op.create_index(
        "ix_diary_events_source",
        "diary_events",
        ["source_type", "source_id"],
    )


def downgrade() -> None:
    """Revert the diary feed redesign schema changes."""
    # -- diary_events --
    op.drop_index("ix_diary_events_source", table_name="diary_events")
    op.drop_index(
        "ix_diary_events_user_occurred", table_name="diary_events",
    )
    op.drop_index("ix_diary_events_user_id", table_name="diary_events")
    op.drop_table("diary_events")

    # -- diary_entries --
    op.drop_index(
        "ix_diary_entries_is_deleted", table_name="diary_entries",
    )
    op.drop_constraint(
        "ck_diary_entry_phase", "diary_entries", type_="check",
    )
    op.drop_constraint(
        "ck_diary_entry_type", "diary_entries", type_="check",
    )
    op.drop_column("diary_entries", "is_deleted")
    op.drop_column("diary_entries", "practice_phase")
    op.drop_column("diary_entries", "entry_type")
