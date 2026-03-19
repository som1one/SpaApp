"""add spa therapy feature content type

Revision ID: 20260319_01
Revises: 20260318_01
Create Date: 2026-03-19
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260319_01"
down_revision = "20260318_01"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()

    bind.execute(
        sa.text(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1
                    FROM pg_enum
                    WHERE enumlabel = 'spa_therapy_feature'
                      AND enumtypid = 'contentblocktype'::regtype
                ) THEN
                    ALTER TYPE contentblocktype ADD VALUE 'spa_therapy_feature';
                END IF;
            END
            $$;
            """
        )
    )

    defaults = [
        (
            "Подарочные сертификаты",
            "Идеальный подарок для близких",
            "https://prirodaspa.ru/gift-sertificate",
            0,
        ),
        (
            "Спа-меню",
            "Выгодные условия на курсы процедур",
            "https://prirodaspa.ru/spa-menu",
            1,
        ),
        (
            "Каталог товаров",
            "Профессиональная косметика для дома",
            "https://priroda-therapy.ru/priroda-spa-catalog",
            2,
        ),
    ]

    for title, subtitle, action_url, order_index in defaults:
        bind.execute(
            sa.text(
                """
                INSERT INTO custom_content_blocks
                    (title, subtitle, action_url, block_type, order_index, is_active, created_at, updated_at)
                SELECT
                    :title, :subtitle, :action_url, 'spa_therapy_feature', :order_index, true, now(), now()
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM custom_content_blocks
                    WHERE block_type = 'spa_therapy_feature'
                      AND order_index = :order_index
                );
                """
            ),
            {
                "title": title,
                "subtitle": subtitle,
                "action_url": action_url,
                "order_index": order_index,
            },
        )


def downgrade():
    # Значение ENUM безопасно не удаляем, чтобы не ломать существующие данные.
    pass
