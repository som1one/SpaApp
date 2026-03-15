"""add_cashback_percent_to_loyalty_levels

Revision ID: a131aa044026
Revises: 5501de4c1d91
Create Date: 2025-11-21 17:04:36.158730

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a131aa044026'
down_revision: Union[str, None] = '5501de4c1d91'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Проверяем существование колонки cashback_percent в таблице loyalty_levels
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Проверяем существование таблицы
    existing_tables = inspector.get_table_names()
    if 'loyalty_levels' not in existing_tables:
        print("- Таблица loyalty_levels не существует, пропускаем миграцию")
        return
    
    # Получаем список колонок
    columns = {col['name']: col for col in inspector.get_columns('loyalty_levels')}
    
    if 'cashback_percent' not in columns:
        # Добавляем колонку cashback_percent
        op.add_column('loyalty_levels', sa.Column('cashback_percent', sa.Integer(), nullable=True))
        print("✓ Добавлена колонка cashback_percent в таблицу loyalty_levels")
        
        # Устанавливаем значения по умолчанию для существующих уровней
        # Бронза (0 баллов) - 3%
        op.execute("""
            UPDATE loyalty_levels 
            SET cashback_percent = 3 
            WHERE min_points = 0 AND (cashback_percent IS NULL OR cashback_percent = 0)
        """)
        
        # Серебро (100 баллов) - 5%
        op.execute("""
            UPDATE loyalty_levels 
            SET cashback_percent = 5 
            WHERE min_points = 100 AND (cashback_percent IS NULL OR cashback_percent = 0)
        """)
        
        # Золото (500 баллов) - 7%
        op.execute("""
            UPDATE loyalty_levels 
            SET cashback_percent = 7 
            WHERE min_points = 500 AND (cashback_percent IS NULL OR cashback_percent = 0)
        """)
        
        # Алмаз (1000 баллов) - 10%
        op.execute("""
            UPDATE loyalty_levels 
            SET cashback_percent = 10 
            WHERE min_points = 1000 AND (cashback_percent IS NULL OR cashback_percent = 0)
        """)
        
        # Для остальных уровней устанавливаем 3% по умолчанию
        op.execute("""
            UPDATE loyalty_levels 
            SET cashback_percent = 3 
            WHERE cashback_percent IS NULL
        """)
        
        # Теперь делаем колонку NOT NULL
        op.alter_column('loyalty_levels', 'cashback_percent', nullable=False)
        print("✓ Установлены значения cashback_percent для существующих уровней")
    else:
        print("- Колонка cashback_percent уже существует в таблице loyalty_levels")


def downgrade() -> None:
    # Удаляем колонку cashback_percent
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    existing_tables = inspector.get_table_names()
    if 'loyalty_levels' not in existing_tables:
        return
    
    columns = [col['name'] for col in inspector.get_columns('loyalty_levels')]
    
    if 'cashback_percent' in columns:
        op.drop_column('loyalty_levels', 'cashback_percent')
        print("✓ Удалена колонка cashback_percent из таблицы loyalty_levels")
