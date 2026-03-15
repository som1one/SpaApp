"""add loyalty fields to bookings table

Revision ID: 20241220_01
Revises: c32c8d3e066d
Create Date: 2025-12-20 12:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20241220_01"
down_revision: Union[str, None] = "c32c8d3e066d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Проверяем существование колонок перед добавлением
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = {col['name']: col for col in inspector.get_columns('bookings')}
    
    # Добавляем loyalty_points_awarded если его нет
    if 'loyalty_points_awarded' not in columns:
        op.add_column(
            'bookings',
            sa.Column(
                'loyalty_points_awarded',
                sa.Boolean(),
                nullable=False,
                server_default=sa.sql.expression.false()
            )
        )
        print("✓ Добавлена колонка loyalty_points_awarded в таблицу bookings")
    else:
        print("- Колонка loyalty_points_awarded уже существует в таблице bookings")
    
    # Добавляем loyalty_points_amount если его нет
    if 'loyalty_points_amount' not in columns:
        op.add_column(
            'bookings',
            sa.Column(
                'loyalty_points_amount',
                sa.Integer(),
                nullable=True
            )
        )
        print("✓ Добавлена колонка loyalty_points_amount в таблицу bookings")
    else:
        print("- Колонка loyalty_points_amount уже существует в таблице bookings")


def downgrade() -> None:
    # Удаляем колонки при откате
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('bookings')]
    
    if 'loyalty_points_amount' in columns:
        op.drop_column('bookings', 'loyalty_points_amount')
    
    if 'loyalty_points_awarded' in columns:
        op.drop_column('bookings', 'loyalty_points_awarded')

