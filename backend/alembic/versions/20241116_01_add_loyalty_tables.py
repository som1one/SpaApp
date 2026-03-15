"""add loyalty levels and bonuses tables

Revision ID: 20241116_01
Revises: 20241115_07
Create Date: 2025-11-16 12:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20241116_01"
down_revision: Union[str, None] = "20241115_07"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'loyalty_levels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('min_points', sa.Integer(), nullable=False),
        sa.Column('color_start', sa.String(length=7), nullable=False),
        sa.Column('color_end', sa.String(length=7), nullable=False),
        sa.Column('icon', sa.String(length=50), nullable=False, server_default='eco'),
        sa.Column('order_index', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.sql.expression.true()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    op.create_table(
        'loyalty_bonuses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('icon', sa.String(length=50), nullable=False, server_default='card_giftcard'),
        sa.Column('level_id', sa.Integer(), nullable=True),
        sa.Column('min_level_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.sql.expression.true()),
        sa.Column('order_index', sa.Integer(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['level_id'], ['loyalty_levels.id'], ),
        sa.ForeignKeyConstraint(['min_level_id'], ['loyalty_levels.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('loyalty_bonuses')
    op.drop_table('loyalty_levels')

