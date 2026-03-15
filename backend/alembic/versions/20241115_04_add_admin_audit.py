"""add admin audit table

Revision ID: 20241115_04
Revises: 20241115_03
Create Date: 2025-11-15 14:30:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20241115_04"
down_revision: Union[str, None] = "20241115_03"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "admin_audit",
        sa.Column("admin_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("entity", sa.String(length=100), nullable=True),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("user_agent", sa.String(length=255), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("executed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["admin_id"], ["admins.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_admin_audit_id"), "admin_audit", ["id"], unique=False)
    op.create_index(op.f("ix_admin_audit_admin_id"), "admin_audit", ["admin_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_admin_audit_admin_id"), table_name="admin_audit")
    op.drop_index(op.f("ix_admin_audit_id"), table_name="admin_audit")
    op.drop_table("admin_audit")

