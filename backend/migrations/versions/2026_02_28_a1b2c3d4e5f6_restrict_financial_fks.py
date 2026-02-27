"""CRITICAL-02: restrict financial foreign keys

Revision ID: a1b2c3d4e5f6
Revises: f2a3b4c5d6e7
Create Date: 2026-02-28

Financial tables (user_ledger, master_ledger, payments, purchases) must
preserve audit trail for 5-year retention. Deleting a parent entity
(user, practice, booking) that has financial records MUST fail.

Changes CASCADE -> RESTRICT on 6 FK constraints:
  - user_ledger.user_id -> users.id
  - master_ledger.user_id -> users.id
  - payments.user_id -> users.id
  - purchases.user_id -> users.id
  - purchases.practice_id -> practices.id
  - purchases.booking_id -> bookings.id
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "f2a3b4c5d6e7"
branch_labels = None
depends_on = None

# (table, constraint_name, column, referenced_table)
_FK_SPECS = [
    ("user_ledger", "user_ledger_user_id_fkey", "user_id", "users.id"),
    ("master_ledger", "master_ledger_user_id_fkey", "user_id", "users.id"),
    ("payments", "payments_user_id_fkey", "user_id", "users.id"),
    ("purchases", "purchases_user_id_fkey", "user_id", "users.id"),
    ("purchases", "purchases_practice_id_fkey", "practice_id", "practices.id"),
    ("purchases", "purchases_booking_id_fkey", "booking_id", "bookings.id"),
]


def upgrade() -> None:
    for table, constraint, column, referent in _FK_SPECS:
        op.drop_constraint(constraint, table, type_="foreignkey")
        op.create_foreign_key(
            constraint,
            table,
            referent.split(".")[0],  # referenced table name
            [column],
            [referent.split(".")[1]],  # referenced column name
            ondelete="RESTRICT",
        )


def downgrade() -> None:
    for table, constraint, column, referent in _FK_SPECS:
        op.drop_constraint(constraint, table, type_="foreignkey")
        op.create_foreign_key(
            constraint,
            table,
            referent.split(".")[0],
            [column],
            [referent.split(".")[1]],
            ondelete="CASCADE",
        )
