"""add notification campaigns table

Revision ID: 20241115_05
Revises: 20241115_04
Create Date: 2025-11-15 15:20:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20241115_05"
down_revision: Union[str, None] = "20241115_04"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "notification_campaigns",
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("channel", sa.Enum("push", "email", "all", name="notificationchannel"), nullable=False, server_default="all"),
        sa.Column("audience", sa.String(length=200), nullable=True),
        sa.Column("status", sa.Enum("draft", "scheduled", "sent", "cancelled", name="notificationstatus"), nullable=False, server_default="draft"),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_admin_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["created_by_admin_id"], ["admins.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notification_campaigns_id"), "notification_campaigns", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_notification_campaigns_id"), table_name="notification_campaigns")
    op.drop_table("notification_campaigns")


