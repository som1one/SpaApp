"""add unique_code to users

Revision ID: 20250124_01
Revises: 20250123_03
Create Date: 2025-01-24

"""
from alembic import op
import sqlalchemy as sa
import secrets


# revision identifiers, used by Alembic.
revision = '20250124_01'
down_revision = '20250123_03'
branch_labels = None
depends_on = None


def generate_unique_code():
    """Генерация уникального кода"""
    return secrets.token_urlsafe(6)[:8].upper().replace('-', '').replace('_', '')


def upgrade():
    # Добавляем колонку unique_code
    op.add_column('users', sa.Column('unique_code', sa.String(length=20), nullable=True))
    
    # Создаем индекс для быстрого поиска
    op.create_index('ix_users_unique_code', 'users', ['unique_code'], unique=True)
    
    # Генерируем уникальные коды для существующих пользователей
    connection = op.get_bind()
    
    # Получаем всех пользователей без кода
    users = connection.execute(sa.text("SELECT id FROM users WHERE unique_code IS NULL")).fetchall()
    
    for user_id, in users:
        # Генерируем уникальный код
        while True:
            code = generate_unique_code()
            # Проверяем уникальность
            existing = connection.execute(
                sa.text("SELECT id FROM users WHERE unique_code = :code"),
                {"code": code}
            ).fetchone()
            if not existing:
                break
        
        # Обновляем пользователя
        connection.execute(
            sa.text("UPDATE users SET unique_code = :code WHERE id = :user_id"),
            {"code": code, "user_id": user_id}
        )
    
    # Делаем колонку NOT NULL после заполнения
    op.alter_column('users', 'unique_code', nullable=False)


def downgrade():
    # Удаляем индекс
    op.drop_index('ix_users_unique_code', table_name='users')
    
    # Удаляем колонку
    op.drop_column('users', 'unique_code')

