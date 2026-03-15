"""create_loyalty_tables

Revision ID: 5501de4c1d91
Revises: 60a244a29737
Create Date: 2025-11-21 16:47:32.277637

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5501de4c1d91'
down_revision: Union[str, None] = '60a244a29737'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Проверяем существование таблиц перед созданием
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()
    
    # Создаем таблицу loyalty_levels если её нет
    if 'loyalty_levels' not in existing_tables:
        op.create_table('loyalty_levels',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('min_points', sa.Integer(), nullable=False),
            sa.Column('cashback_percent', sa.Integer(), nullable=False),
            sa.Column('icon', sa.String(), nullable=True),
            sa.Column('color_start', sa.String(), nullable=True),
            sa.Column('color_end', sa.String(), nullable=True),
            sa.Column('order_index', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_loyalty_levels_id'), 'loyalty_levels', ['id'], unique=False)
        op.create_index(op.f('ix_loyalty_levels_min_points'), 'loyalty_levels', ['min_points'], unique=False)
        print("✓ Создана таблица loyalty_levels")
    else:
        print("- Таблица loyalty_levels уже существует")

    # Создаем таблицу loyalty_bonuses если её нет
    if 'loyalty_bonuses' not in existing_tables:
        op.create_table('loyalty_bonuses',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(), nullable=False),
            sa.Column('description', sa.String(), nullable=True),
            sa.Column('required_level_id', sa.Integer(), nullable=True),
            sa.Column('icon', sa.String(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
            sa.Column('order_index', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['required_level_id'], ['loyalty_levels.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_loyalty_bonuses_id'), 'loyalty_bonuses', ['id'], unique=False)
        print("✓ Создана таблица loyalty_bonuses")
    else:
        print("- Таблица loyalty_bonuses уже существует")

    # Проверяем существование колонок в users перед добавлением
    user_columns = {col['name']: col for col in inspector.get_columns('users')}
    
    if 'loyalty_points' not in user_columns:
        op.add_column('users', sa.Column('loyalty_points', sa.Integer(), nullable=True, server_default='0'))
        print("✓ Добавлена колонка loyalty_points в таблицу users")
    else:
        print("- Колонка loyalty_points уже существует в таблице users")
    
    if 'loyalty_level_id' not in user_columns:
        op.add_column('users', sa.Column('loyalty_level_id', sa.Integer(), nullable=True))
        print("✓ Добавлена колонка loyalty_level_id в таблицу users")
    else:
        print("- Колонка loyalty_level_id уже существует в таблице users")
    
    # Проверяем существование внешнего ключа перед созданием
    foreign_keys = inspector.get_foreign_keys('users')
    fk_exists = any(fk['name'] == 'fk_users_loyalty_level' for fk in foreign_keys)
    
    if not fk_exists and 'loyalty_level_id' in user_columns:
        op.create_foreign_key('fk_users_loyalty_level', 'users', 'loyalty_levels', ['loyalty_level_id'], ['id'])
        print("✓ Создан внешний ключ fk_users_loyalty_level")
    else:
        print("- Внешний ключ fk_users_loyalty_level уже существует")


def downgrade() -> None:
    # Удаляем внешний ключ и поля лояльности из users
    op.drop_constraint('fk_users_loyalty_level', 'users', type_='foreignkey')
    op.drop_column('users', 'loyalty_level_id')
    op.drop_column('users', 'loyalty_points')

    # Удаляем таблицу loyalty_bonuses
    op.drop_index(op.f('ix_loyalty_bonuses_id'), table_name='loyalty_bonuses')
    op.drop_table('loyalty_bonuses')

    # Удаляем таблицу loyalty_levels
    op.drop_index(op.f('ix_loyalty_levels_min_points'), table_name='loyalty_levels')
    op.drop_index(op.f('ix_loyalty_levels_id'), table_name='loyalty_levels')
    op.drop_table('loyalty_levels')
