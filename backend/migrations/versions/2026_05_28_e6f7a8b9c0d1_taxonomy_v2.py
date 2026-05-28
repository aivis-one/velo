# =============================================================================
# Migration: practice taxonomy v2 -- 10 directions, direction-conditional styles
# =============================================================================
# Frontend agreed the final taxonomy on 2026-05-28 (see
# docs/frontend/practice-taxonomy.md). Three legacy directions become
# direction+style pairs:
#
#   direction='womens_circle' -> direction='circles', style='womens'
#   direction='mens_circle'   -> direction='circles', style='mens'
#   direction='kundalini'     -> direction='yoga',    style='kundalini'
#
# (The other five directions — meditation/yoga/breathwork/somatic/tantra —
# stay as-is. The five truly new directions — circles/sound_healing/art/
# narrative/movement — only need the config/enum/schema updates that ship
# with this commit; no rows to backfill.)
#
# Data lives in JSONB Practice.data.taxonomy (schema-on-read sandbox).
# This migration only TOUCHES rows whose taxonomy.direction matches one
# of the three legacy keys — everything else is left alone.
#
# -----------------------------------------------------------------------------
# SQL PREVIEW (human-review BEFORE running on the live DB)
# -----------------------------------------------------------------------------
# upgrade():
#   UPDATE practices SET data = jsonb_set(
#       jsonb_set(data, '{taxonomy,direction}', '"circles"'),
#       '{taxonomy,style}',                     '"womens"'
#   ) WHERE data->'taxonomy'->>'direction' = 'womens_circle';
#
#   UPDATE practices SET data = jsonb_set(
#       jsonb_set(data, '{taxonomy,direction}', '"circles"'),
#       '{taxonomy,style}',                     '"mens"'
#   ) WHERE data->'taxonomy'->>'direction' = 'mens_circle';
#
#   UPDATE practices SET data = jsonb_set(
#       jsonb_set(data, '{taxonomy,direction}', '"yoga"'),
#       '{taxonomy,style}',                     '"kundalini"'
#   ) WHERE data->'taxonomy'->>'direction' = 'kundalini';
#
# downgrade(): reverses each pair (direction+style -> legacy direction).
#   Note: kundalini downgrade only matches rows where BOTH direction='yoga'
#   AND style='kundalini' (real yoga-with-kundalini); style='' would not match.
# -----------------------------------------------------------------------------
# =============================================================================

"""taxonomy_v2

Revision ID: e6f7a8b9c0d1
Revises: d5e6f7a8b9c0
Create Date: 2026-05-28
"""

from collections.abc import Sequence

from alembic import op

revision: str = "e6f7a8b9c0d1"
down_revision: str | None = "d5e6f7a8b9c0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# JSONB UPDATE helpers — jsonb_set is nested because we touch two keys.
# Both arguments to the inner jsonb_set are JSONB values; the new string
# values are wrapped in double quotes to be valid JSON.

_UP_WOMENS = """
UPDATE practices SET data = jsonb_set(
    jsonb_set(data, '{taxonomy,direction}', '"circles"'),
    '{taxonomy,style}', '"womens"'
) WHERE data->'taxonomy'->>'direction' = 'womens_circle';
"""

_UP_MENS = """
UPDATE practices SET data = jsonb_set(
    jsonb_set(data, '{taxonomy,direction}', '"circles"'),
    '{taxonomy,style}', '"mens"'
) WHERE data->'taxonomy'->>'direction' = 'mens_circle';
"""

_UP_KUNDALINI = """
UPDATE practices SET data = jsonb_set(
    jsonb_set(data, '{taxonomy,direction}', '"yoga"'),
    '{taxonomy,style}', '"kundalini"'
) WHERE data->'taxonomy'->>'direction' = 'kundalini';
"""

_DOWN_WOMENS = """
UPDATE practices SET data = jsonb_set(
    jsonb_set(data, '{taxonomy,direction}', '"womens_circle"'),
    '{taxonomy,style}', 'null'::jsonb
) WHERE data->'taxonomy'->>'direction' = 'circles'
  AND data->'taxonomy'->>'style' = 'womens';
"""

_DOWN_MENS = """
UPDATE practices SET data = jsonb_set(
    jsonb_set(data, '{taxonomy,direction}', '"mens_circle"'),
    '{taxonomy,style}', 'null'::jsonb
) WHERE data->'taxonomy'->>'direction' = 'circles'
  AND data->'taxonomy'->>'style' = 'mens';
"""

_DOWN_KUNDALINI = """
UPDATE practices SET data = jsonb_set(
    jsonb_set(data, '{taxonomy,direction}', '"kundalini"'),
    '{taxonomy,style}', 'null'::jsonb
) WHERE data->'taxonomy'->>'direction' = 'yoga'
  AND data->'taxonomy'->>'style' = 'kundalini';
"""


def upgrade() -> None:
    """Remap three legacy directions into direction+style pairs."""
    op.execute(_UP_WOMENS)
    op.execute(_UP_MENS)
    op.execute(_UP_KUNDALINI)


def downgrade() -> None:
    """Reverse the v2 remap. Only touches rows that look v2-shaped."""
    op.execute(_DOWN_WOMENS)
    op.execute(_DOWN_MENS)
    op.execute(_DOWN_KUNDALINI)
