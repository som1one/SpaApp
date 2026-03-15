"""add_loyalty_fields_to_users

Revision ID: ff0b41366a28
Revises: 20241116_03
Create Date: 2025-11-18 18:03:50.548770

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff0b41366a28'
down_revision: Union[str, None] = '20241116_03'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Проверяем существование колонок перед добавлением
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = {col['name']: col for col in inspector.get_columns('users')}
    
    # Добавляем loyalty_level если его нет
    if 'loyalty_level' not in columns:
        op.add_column('users', sa.Column('loyalty_level', sa.Integer(), nullable=False, server_default='1'))
    else:
        # Если колонка есть, но нет default, добавляем его
        col_info = columns['loyalty_level']
        if col_info.get('default') is None:
            op.alter_column('users', 'loyalty_level', 
                           server_default='1', 
                           existing_type=sa.Integer(), 
                           existing_nullable=False)
    
    # Добавляем auto_apply_loyalty_points если его нет
    if 'auto_apply_loyalty_points' not in columns:
        op.add_column('users', sa.Column('auto_apply_loyalty_points', sa.Boolean(), nullable=False, server_default=sa.sql.expression.false()))


def downgrade() -> None:
    # Удаляем колонки при откате
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    if 'auto_apply_loyalty_points' in columns:
        op.drop_column('users', 'auto_apply_loyalty_points')
    
    # loyalty_level не удаляем, так как он был в init_schema
