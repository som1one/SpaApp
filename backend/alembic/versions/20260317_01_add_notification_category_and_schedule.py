"""add notification category and scheduled_at

Revision ID: 20260317_01
Revises: 20250124_01
Create Date: 2026-03-17
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260317_01"
down_revision = "20250124_01"
branch_labels = None
depends_on = None


def _column_names(table_name: str) -> set[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    existing_columns = _column_names("notification_campaigns")

    if "category" not in existing_columns:
        op.add_column(
            "notification_campaigns",
            sa.Column("category", sa.String(length=50), nullable=False, server_default="general"),
        )

    if "scheduled_at" not in existing_columns:
        op.add_column(
            "notification_campaigns",
            sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        )


def downgrade() -> None:
    existing_columns = _column_names("notification_campaigns")

    if "scheduled_at" in existing_columns:
        op.drop_column("notification_campaigns", "scheduled_at")

    if "category" in existing_columns:
        op.drop_column("notification_campaigns", "category")
