"""add loyalty settings and history

Revision ID: 20260318_01_add_loyalty_settings_and_history
Revises: 20260317_01
Create Date: 2026-03-18 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260318_01_add_loyalty_settings_and_history"
down_revision = "20260317_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "loyalty_program_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("loyalty_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("points_per_100_rub", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("welcome_bonus_amount", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("bonus_expiry_days", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("yclients_bonus_field_id", sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_loyalty_program_settings_id"),
        "loyalty_program_settings",
        ["id"],
        unique=False,
    )

    op.create_table(
        "loyalty_transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("booking_id", sa.Integer(), nullable=True),
        sa.Column("source_transaction_id", sa.Integer(), nullable=True),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("transaction_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="active"),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expired_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["source_transaction_id"], ["loyalty_transactions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_loyalty_transactions_id"), "loyalty_transactions", ["id"], unique=False)
    op.create_index(op.f("ix_loyalty_transactions_user_id"), "loyalty_transactions", ["user_id"], unique=False)
    op.create_index(op.f("ix_loyalty_transactions_booking_id"), "loyalty_transactions", ["booking_id"], unique=False)
    op.create_index(
        op.f("ix_loyalty_transactions_source_transaction_id"),
        "loyalty_transactions",
        ["source_transaction_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_loyalty_transactions_transaction_type"),
        "loyalty_transactions",
        ["transaction_type"],
        unique=False,
    )
    op.create_index(op.f("ix_loyalty_transactions_status"), "loyalty_transactions", ["status"], unique=False)
    op.create_index(op.f("ix_loyalty_transactions_expires_at"), "loyalty_transactions", ["expires_at"], unique=False)

    op.execute(
        """
        INSERT INTO loyalty_program_settings
            (id, loyalty_enabled, points_per_100_rub, welcome_bonus_amount, bonus_expiry_days)
        VALUES
            (1, true, 5, 0, 30)
        """
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_loyalty_transactions_expires_at"), table_name="loyalty_transactions")
    op.drop_index(op.f("ix_loyalty_transactions_status"), table_name="loyalty_transactions")
    op.drop_index(op.f("ix_loyalty_transactions_transaction_type"), table_name="loyalty_transactions")
    op.drop_index(op.f("ix_loyalty_transactions_source_transaction_id"), table_name="loyalty_transactions")
    op.drop_index(op.f("ix_loyalty_transactions_booking_id"), table_name="loyalty_transactions")
    op.drop_index(op.f("ix_loyalty_transactions_user_id"), table_name="loyalty_transactions")
    op.drop_index(op.f("ix_loyalty_transactions_id"), table_name="loyalty_transactions")
    op.drop_table("loyalty_transactions")

    op.drop_index(op.f("ix_loyalty_program_settings_id"), table_name="loyalty_program_settings")
    op.drop_table("loyalty_program_settings")
