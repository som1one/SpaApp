"""add role and invited_by_admin_id to admin_invites

Revision ID: 20250123_03
Revises: 20250123_02
Create Date: 2025-01-23

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20250123_03'
down_revision = '20250123_02'
branch_labels = None
depends_on = None


def upgrade():
    # Проверяем существование колонок перед добавлением
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('admin_invites')]
    
    # Добавляем колонку role, если её нет
    if 'role' not in columns:
        op.add_column('admin_invites', sa.Column('role', sa.String(length=50), nullable=False, server_default='admin'))
        # Убираем server_default после добавления
        op.alter_column('admin_invites', 'role', server_default=None)
    
    # Добавляем колонку invited_by_admin_id, если её нет
    if 'invited_by_admin_id' not in columns:
        op.add_column('admin_invites', sa.Column('invited_by_admin_id', sa.Integer(), nullable=True))
        # Проверяем существование foreign key перед созданием
        foreign_keys = [fk['name'] for fk in inspector.get_foreign_keys('admin_invites')]
        if 'fk_admin_invites_invited_by' not in foreign_keys and 'fk_admin_invites_invited_by_admin_id' not in foreign_keys:
            op.create_foreign_key(
                'fk_admin_invites_invited_by',
                'admin_invites',
                'admins',
                ['invited_by_admin_id'],
                ['id'],
                ondelete='SET NULL'
            )


def downgrade():
    # Удаляем foreign key
    try:
        op.drop_constraint('fk_admin_invites_invited_by_admin_id', 'admin_invites', type_='foreignkey')
    except Exception:
        pass
    
    # Удаляем колонки
    try:
        op.drop_column('admin_invites', 'invited_by_admin_id')
    except Exception:
        pass
    
    try:
        op.drop_column('admin_invites', 'role')
    except Exception:
        pass

