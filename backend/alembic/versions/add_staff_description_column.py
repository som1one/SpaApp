"""add staff description column and staff_services is_active

Revision ID: add_staff_desc
Revises: 3a909126af47
Create Date: 2025-11-21 18:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_staff_desc'
down_revision: Union[str, None] = '3a909126af47'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Проверяем существование колонок в таблицах staff и staff_services
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Проверяем существование таблиц
    existing_tables = inspector.get_table_names()
    
    # Обновляем таблицу staff
    if 'staff' in existing_tables:
        staff_columns = {col['name']: col for col in inspector.get_columns('staff')}
        
        # Добавляем колонку description если её нет
        if 'description' not in staff_columns:
            op.add_column('staff', sa.Column('description', sa.String(1000), nullable=True))
            print("✓ Добавлена колонка description в таблицу staff")
        else:
            print("- Колонка description уже существует в таблице staff")
        
        # Добавляем колонку specialization если её нет (на всякий случай)
        if 'specialization' not in staff_columns:
            op.add_column('staff', sa.Column('specialization', sa.String(500), nullable=True))
            print("✓ Добавлена колонка specialization в таблицу staff")
        else:
            print("- Колонка specialization уже существует в таблице staff")
    else:
        print("- Таблица staff не существует, пропускаем")
    
    # Обновляем таблицу staff_services
    if 'staff_services' in existing_tables:
        staff_services_columns = {col['name']: col for col in inspector.get_columns('staff_services')}
        
        # Добавляем колонку is_active если её нет
        if 'is_active' not in staff_services_columns:
            op.add_column('staff_services', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
            print("✓ Добавлена колонка is_active в таблицу staff_services")
        else:
            print("- Колонка is_active уже существует в таблице staff_services")
    else:
        print("- Таблица staff_services не существует, пропускаем")


def downgrade() -> None:
    # Удаляем добавленные колонки
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    existing_tables = inspector.get_table_names()
    
    # Удаляем колонки из staff
    if 'staff' in existing_tables:
        staff_columns = [col['name'] for col in inspector.get_columns('staff')]
        
        if 'description' in staff_columns:
            op.drop_column('staff', 'description')
            print("✓ Удалена колонка description из таблицы staff")
        
        if 'specialization' in staff_columns:
            op.drop_column('staff', 'specialization')
            print("✓ Удалена колонка specialization из таблицы staff")
    
    # Удаляем колонку из staff_services
    if 'staff_services' in existing_tables:
        staff_services_columns = [col['name'] for col in inspector.get_columns('staff_services')]
        
        if 'is_active' in staff_services_columns:
            op.drop_column('staff_services', 'is_active')
            print("✓ Удалена колонка is_active из таблицы staff_services")

