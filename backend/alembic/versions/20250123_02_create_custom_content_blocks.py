"""create custom content blocks

Revision ID: 20250123_02
Revises: 20250123_01
Create Date: 2025-01-23

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '20250123_02'
down_revision = '20250123_01'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()

    # 1. Убедиться, что тип ENUM существует (создаём один раз вручную)
    exists = bind.execute(
        sa.text("SELECT 1 FROM pg_type WHERE typname = 'contentblocktype'")
    ).scalar()

    if not exists:
        enum_type = postgresql.ENUM(
            'spa_travel',
            'promotion',
            'banner',
            'custom',
            name='contentblocktype',
        )
        enum_type.create(bind, checkfirst=False)

    # 2. Тип для колонки, который НЕ будет пытаться делать CREATE TYPE ещё раз
    content_block_type_enum = postgresql.ENUM(
        'spa_travel',
        'promotion',
        'banner',
        'custom',
        name='contentblocktype',
        create_type=False,
    )

    # Создаем таблицу custom_content_blocks
    op.create_table(
        'custom_content_blocks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('subtitle', sa.String(length=300), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('action_url', sa.String(length=500), nullable=True),
        sa.Column('action_text', sa.String(length=100), nullable=True),
        sa.Column('block_type', content_block_type_enum, nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('background_color', sa.String(length=7), nullable=True),
        sa.Column('text_color', sa.String(length=7), nullable=True),
        sa.Column('gradient_start', sa.String(length=7), nullable=True),
        sa.Column('gradient_end', sa.String(length=7), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_custom_content_blocks_id'), 'custom_content_blocks', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_custom_content_blocks_id'), table_name='custom_content_blocks')
    op.drop_table('custom_content_blocks')
    # Удаляем ENUM тип (если больше нигде не используется)
    sa.Enum(name='contentblocktype').drop(op.get_bind(), checkfirst=True)

