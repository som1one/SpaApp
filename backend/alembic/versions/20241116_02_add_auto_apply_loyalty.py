"""add auto_apply_loyalty_points to users

Revision ID: 20241116_02
Revises: 20241116_01
Create Date: 2025-11-16 13:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20241116_02"
down_revision: Union[str, None] = "20241116_01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('auto_apply_loyalty_points', sa.Boolean(), nullable=False, server_default=sa.sql.expression.false()))


def downgrade() -> None:
    op.drop_column('users', 'auto_apply_loyalty_points')

