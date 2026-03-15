"""rename points to bonuses

Revision ID: 20250123_01
Revises: 
Create Date: 2025-01-23

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20250123_01'
down_revision = '653b009841e0'  # Последняя ревизия
branch_labels = None
depends_on = None


def upgrade():
    # Переименование колонок в таблице users
    op.alter_column('users', 'loyalty_points', new_column_name='loyalty_bonuses', existing_type=sa.Integer(), existing_nullable=False)
    
    # Добавление колонки spent_bonuses в таблицу users
    op.add_column('users', sa.Column('spent_bonuses', sa.Integer(), nullable=False, server_default='0'))
    
    # Переименование колонок в таблице loyalty_levels
    op.alter_column('loyalty_levels', 'min_points', new_column_name='min_bonuses', existing_type=sa.Integer(), existing_nullable=False)
    
    # Переименование колонок в таблице bookings
    op.alter_column('bookings', 'loyalty_points_awarded', new_column_name='loyalty_bonuses_awarded', existing_type=sa.Boolean(), existing_nullable=False)
    op.alter_column('bookings', 'loyalty_points_amount', new_column_name='loyalty_bonuses_amount', existing_type=sa.Integer(), existing_nullable=True)


def downgrade():
    # Откат изменений в таблице bookings
    op.alter_column('bookings', 'loyalty_bonuses_awarded', new_column_name='loyalty_points_awarded', existing_type=sa.Boolean(), existing_nullable=False)
    op.alter_column('bookings', 'loyalty_bonuses_amount', new_column_name='loyalty_points_amount', existing_type=sa.Integer(), existing_nullable=True)
    
    # Откат изменений в таблице loyalty_levels
    op.alter_column('loyalty_levels', 'min_bonuses', new_column_name='min_points', existing_type=sa.Integer(), existing_nullable=False)
    
    # Удаление колонки spent_bonuses из таблицы users
    op.drop_column('users', 'spent_bonuses')
    
    # Откат изменений в таблице users
    op.alter_column('users', 'loyalty_bonuses', new_column_name='loyalty_points', existing_type=sa.Integer(), existing_nullable=False)

