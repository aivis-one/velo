# =============================================================================
# Migration: mood / rating from enum string to 1..10 integer score
# =============================================================================
# Check-in mood, feedback rating and diary-entry mood were stored as short
# enum strings (low/mid/high, fire/good/confused) guarded by IN (...) check
# constraints. They become 1..10 integer scores (slider) guarded by
# BETWEEN 1 AND 10. The UI derives the icon/label from the range
# (1-3 / 4-7 / 8-10).
#
# Affected columns:
#   checkins.mood        VARCHAR -> INTEGER, NOT NULL
#   feedbacks.rating     VARCHAR -> INTEGER, NOT NULL
#   diary_entries.mood   VARCHAR -> INTEGER, NULL allowed
#
# The DB is wiped each deploy and the test DB is built from scratch by
# running migrations on an empty database, so the tables are empty when this
# runs. The USING clause maps any stray old string values to a sensible
# mid-range score anyway (low/confused -> 2, mid/good -> 6, high/fire -> 9)
# so the cast never fails and never violates the new BETWEEN constraint.
# =============================================================================

"""mood_rating_to_score

Revision ID: d5e6f7a8b9c0
Revises: c4d5e6f7a8b9
Create Date: 2026-05-27
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d5e6f7a8b9c0"
down_revision: str | None = "c4d5e6f7a8b9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# USING expressions: map legacy enum strings to a mid-range integer score.
# Empty tables make these no-ops; defensive for any stray rows.
_MOOD_USING = (
    "(CASE mood "
    "WHEN 'low' THEN 2 WHEN 'mid' THEN 6 WHEN 'high' THEN 9 "
    "ELSE 5 END)"
)
_RATING_USING = (
    "(CASE rating "
    "WHEN 'confused' THEN 2 WHEN 'good' THEN 6 WHEN 'fire' THEN 9 "
    "ELSE 5 END)"
)
# diary_entries.mood is nullable: keep NULL as NULL.
_DIARY_MOOD_USING = (
    "(CASE WHEN mood IS NULL THEN NULL "
    "WHEN mood = 'low' THEN 2 WHEN mood = 'mid' THEN 6 "
    "WHEN mood = 'high' THEN 9 ELSE 5 END)"
)


def upgrade() -> None:
    """Convert mood/rating to 1..10 integer scores."""
    # -- checkins.mood --
    op.drop_constraint("ck_checkin_mood", "checkins", type_="check")
    op.alter_column(
        "checkins",
        "mood",
        existing_type=sa.String(length=10),
        type_=sa.Integer(),
        existing_nullable=False,
        postgresql_using=_MOOD_USING,
    )
    op.create_check_constraint(
        "ck_checkin_mood",
        "checkins",
        "mood BETWEEN 1 AND 10",
    )

    # -- feedbacks.rating --
    op.drop_constraint("ck_feedback_rating", "feedbacks", type_="check")
    op.alter_column(
        "feedbacks",
        "rating",
        existing_type=sa.String(length=10),
        type_=sa.Integer(),
        existing_nullable=False,
        postgresql_using=_RATING_USING,
    )
    op.create_check_constraint(
        "ck_feedback_rating",
        "feedbacks",
        "rating BETWEEN 1 AND 10",
    )

    # -- diary_entries.mood (nullable) --
    op.drop_constraint("ck_diary_entry_mood", "diary_entries", type_="check")
    op.alter_column(
        "diary_entries",
        "mood",
        existing_type=sa.String(length=10),
        type_=sa.Integer(),
        existing_nullable=True,
        postgresql_using=_DIARY_MOOD_USING,
    )
    op.create_check_constraint(
        "ck_diary_entry_mood",
        "diary_entries",
        "mood IS NULL OR mood BETWEEN 1 AND 10",
    )


def downgrade() -> None:
    """Revert mood/rating back to enum strings.

    Reverse map: 1-3 -> low/confused, 4-7 -> mid/good, 8-10 -> fire/high.
    """
    # -- diary_entries.mood --
    op.drop_constraint("ck_diary_entry_mood", "diary_entries", type_="check")
    op.alter_column(
        "diary_entries",
        "mood",
        existing_type=sa.Integer(),
        type_=sa.String(length=10),
        existing_nullable=True,
        postgresql_using=(
            "(CASE WHEN mood IS NULL THEN NULL "
            "WHEN mood <= 3 THEN 'low' WHEN mood <= 7 THEN 'mid' "
            "ELSE 'high' END)"
        ),
    )
    op.create_check_constraint(
        "ck_diary_entry_mood",
        "diary_entries",
        "mood IS NULL OR mood IN ('low', 'mid', 'high')",
    )

    # -- feedbacks.rating --
    op.drop_constraint("ck_feedback_rating", "feedbacks", type_="check")
    op.alter_column(
        "feedbacks",
        "rating",
        existing_type=sa.Integer(),
        type_=sa.String(length=10),
        existing_nullable=False,
        postgresql_using=(
            "(CASE WHEN rating <= 3 THEN 'confused' "
            "WHEN rating <= 7 THEN 'good' ELSE 'fire' END)"
        ),
    )
    op.create_check_constraint(
        "ck_feedback_rating",
        "feedbacks",
        "rating IN ('fire', 'good', 'confused')",
    )

    # -- checkins.mood --
    op.drop_constraint("ck_checkin_mood", "checkins", type_="check")
    op.alter_column(
        "checkins",
        "mood",
        existing_type=sa.Integer(),
        type_=sa.String(length=10),
        existing_nullable=False,
        postgresql_using=(
            "(CASE WHEN mood <= 3 THEN 'low' "
            "WHEN mood <= 7 THEN 'mid' ELSE 'high' END)"
        ),
    )
    op.create_check_constraint(
        "ck_checkin_mood",
        "checkins",
        "mood IN ('low', 'mid', 'high')",
    )
