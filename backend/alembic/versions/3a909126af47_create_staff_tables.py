"""create_staff_tables

Revision ID: 3a909126af47
Revises: 333e8be2da6c
Create Date: 2025-11-21 17:18:01.149745

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3a909126af47'
down_revision: Union[str, None] = 'a131aa044026'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Проверяем существование таблиц перед созданием
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()
    
    # Создаем таблицу staff если её нет
    if 'staff' not in existing_tables:
        op.create_table('staff',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(200), nullable=False),
            sa.Column('surname', sa.String(200), nullable=True),
            sa.Column('phone', sa.String(20), nullable=True),
            sa.Column('email', sa.String(255), nullable=True),
            sa.Column('specialization', sa.String(500), nullable=True),
            sa.Column('photo_url', sa.String(500), nullable=True),
            sa.Column('description', sa.String(1000), nullable=True),
            sa.Column('yclients_staff_id', sa.Integer(), nullable=True, unique=True),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('order_index', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_staff_id'), 'staff', ['id'], unique=False)
        print("✓ Создана таблица staff")
    else:
        print("- Таблица staff уже существует")
        # Проверяем и добавляем недостающие колонки
        staff_columns = {col['name']: col for col in inspector.get_columns('staff')}
        
        if 'description' not in staff_columns:
            op.add_column('staff', sa.Column('description', sa.String(1000), nullable=True))
            print("✓ Добавлена колонка description в таблицу staff")
        
        if 'specialization' not in staff_columns:
            op.add_column('staff', sa.Column('specialization', sa.String(500), nullable=True))
            print("✓ Добавлена колонка specialization в таблицу staff")
    
    # Создаем таблицу staff_schedules если её нет
    if 'staff_schedules' not in existing_tables:
        op.create_table('staff_schedules',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('staff_id', sa.Integer(), nullable=False),
            sa.Column('day_of_week', sa.Integer(), nullable=False),
            sa.Column('start_time', sa.Time(), nullable=False),
            sa.Column('end_time', sa.Time(), nullable=False),
            sa.Column('break_start', sa.Time(), nullable=True),
            sa.Column('break_end', sa.Time(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['staff_id'], ['staff.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_staff_schedules_id'), 'staff_schedules', ['id'], unique=False)
        print("✓ Создана таблица staff_schedules")
    else:
        print("- Таблица staff_schedules уже существует")
    
    # Создаем таблицу staff_services если её нет
    if 'staff_services' not in existing_tables:
        op.create_table('staff_services',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('staff_id', sa.Integer(), nullable=False),
            sa.Column('service_id', sa.Integer(), nullable=False),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['staff_id'], ['staff.id'], ),
            sa.ForeignKeyConstraint(['service_id'], ['services.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('staff_id', 'service_id', name='uq_staff_service')
        )
        op.create_index(op.f('ix_staff_services_id'), 'staff_services', ['id'], unique=False)
        print("✓ Создана таблица staff_services")
    else:
        print("- Таблица staff_services уже существует")


def downgrade() -> None:
    # Удаляем таблицы в обратном порядке
    op.drop_index(op.f('ix_staff_services_id'), table_name='staff_services')
    op.drop_table('staff_services')
    
    op.drop_index(op.f('ix_staff_schedules_id'), table_name='staff_schedules')
    op.drop_table('staff_schedules')
    
    op.drop_index(op.f('ix_staff_id'), table_name='staff')
    op.drop_table('staff')
