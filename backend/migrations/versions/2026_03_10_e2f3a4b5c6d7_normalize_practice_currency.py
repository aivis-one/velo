# =============================================================================
# Migration: Normalize practices.currency to lowercase (NEW-7)
# =============================================================================
# 1. ALTER COLUMN server_default: 'EUR' -> 'eur'
# 2. UPDATE existing rows: SET currency = 'eur' WHERE currency = 'EUR'
#
# Background: practices.currency was created with server_default='EUR'
# (migration d4e5f6a7b8c9). All other payment tables (payments, purchases,
# withdrawals) use lowercase 'eur'. This migration normalizes practices to
# match, preventing inconsistency in Stripe API calls and semaphore checks.
#
# Data migration is safe: only affects display/comparison consistency.
# Stripe accepts both 'EUR' and 'eur'; lowercase is the canonical form
# per Stripe documentation.
# =============================================================================

"""normalize_practice_currency_to_lowercase

Revision ID: e2f3a4b5c6d7
Revises: d1e2f3a4b5c6
Create Date: 2026-03-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e2f3a4b5c6d7"
down_revision: str | None = "d1e2f3a4b5c6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Normalize practices.currency server_default and existing data."""
    # Step 1: Update server_default from 'EUR' to 'eur'.
    op.alter_column(
        "practices",
        "currency",
        server_default="eur",
        existing_type=sa.String(3),
        existing_nullable=False,
    )

    # Step 2: Normalize existing rows.
    # Uses execute() with text() -- raw UPDATE is acceptable here because
    # this is a data migration with no ORM model available at migration time.
    op.execute(
        sa.text("UPDATE practices SET currency = 'eur' WHERE currency = 'EUR'")
    )


def downgrade() -> None:
    """Revert server_default to uppercase and restore existing data."""
    op.alter_column(
        "practices",
        "currency",
        server_default="EUR",
        existing_type=sa.String(3),
        existing_nullable=False,
    )

    op.execute(
        sa.text("UPDATE practices SET currency = 'EUR' WHERE currency = 'eur'")
    )
