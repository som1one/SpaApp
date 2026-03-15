"""add role and invited_by to admin_invites

Revision ID: 20241115_01
Revises: 20241114_02
Create Date: 2025-11-15 10:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20241115_01"
down_revision: Union[str, None] = "20241114_02"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "admin_invites",
        sa.Column("role", sa.String(length=50), nullable=False, server_default="admin"),
    )
    op.add_column(
        "admin_invites",
        sa.Column("invited_by_admin_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_admin_invites_invited_by",
        "admin_invites",
        "admins",
        ["invited_by_admin_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.alter_column("admin_invites", "role", server_default=None)


def downgrade() -> None:
    op.drop_constraint("fk_admin_invites_invited_by", "admin_invites", type_="foreignkey")
    op.drop_column("admin_invites", "invited_by_admin_id")
    op.drop_column("admin_invites", "role")


