"""add admins and invites tables

Revision ID: 20241114_02
Revises: 20241114_01
Create Date: 2025-11-14 15:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = '20241114_02'
down_revision = '20241114_01'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'admins',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='admin'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.sql.expression.true()),
        sa.Column('invited_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_admins_email'), 'admins', ['email'], unique=True)

    op.create_table(
        'admin_invites',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('token', sa.String(length=64), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('accepted', sa.Boolean(), nullable=False, server_default=sa.sql.expression.false()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('token')
    )


def downgrade() -> None:
    op.drop_table('admin_invites')
    op.drop_index(op.f('ix_admins_email'), table_name='admins')
    op.drop_table('admins')


