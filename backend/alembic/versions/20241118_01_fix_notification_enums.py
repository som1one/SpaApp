"""fix notification enums to use string

Revision ID: 20241118_01
Revises: ff0b41366a28
Create Date: 2025-11-18 19:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20241118_01'
down_revision: Union[str, None] = '9128530ec343'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Сначала удаляем default значения, которые зависят от enum
    op.alter_column('notification_campaigns', 'channel',
                    server_default=None,
                    existing_type=sa.Enum('push', 'email', 'all', name='notificationchannel'))
    op.alter_column('notification_campaigns', 'status',
                    server_default=None,
                    existing_type=sa.Enum('draft', 'scheduled', 'sent', 'cancelled', name='notificationstatus'))
    
    # Теперь изменяем тип колонок с enum на VARCHAR
    op.alter_column('notification_campaigns', 'channel',
                    type_=sa.String(50),
                    existing_type=sa.Enum('push', 'email', 'all', name='notificationchannel'),
                    postgresql_using='channel::text')
    op.alter_column('notification_campaigns', 'status',
                    type_=sa.String(50),
                    existing_type=sa.Enum('draft', 'scheduled', 'sent', 'cancelled', name='notificationstatus'),
                    postgresql_using='status::text')
    
    # Удаляем enum типы, так как они больше не используются
    op.execute('DROP TYPE IF EXISTS notificationchannel')
    op.execute('DROP TYPE IF EXISTS notificationstatus')
    
    # Восстанавливаем default значения как строки
    op.alter_column('notification_campaigns', 'channel',
                    server_default='all',
                    existing_type=sa.String(50))
    op.alter_column('notification_campaigns', 'status',
                    server_default='draft',
                    existing_type=sa.String(50))


def downgrade() -> None:
    # Удаляем string default значения
    op.alter_column('notification_campaigns', 'channel',
                    server_default=None,
                    existing_type=sa.String(50))
    op.alter_column('notification_campaigns', 'status',
                    server_default=None,
                    existing_type=sa.String(50))
    
    # Создаем enum типы обратно
    op.execute("CREATE TYPE notificationchannel AS ENUM ('push', 'email', 'all')")
    op.execute("CREATE TYPE notificationstatus AS ENUM ('draft', 'scheduled', 'sent', 'cancelled')")
    
    # Изменяем тип колонок обратно на enum
    op.alter_column('notification_campaigns', 'channel',
                    type_=sa.Enum('push', 'email', 'all', name='notificationchannel'),
                    existing_type=sa.String(50),
                    postgresql_using='channel::notificationchannel')
    op.alter_column('notification_campaigns', 'status',
                    type_=sa.Enum('draft', 'scheduled', 'sent', 'cancelled', name='notificationstatus'),
                    existing_type=sa.String(50),
                    postgresql_using='status::notificationstatus')
    
    # Восстанавливаем enum default значения
    op.alter_column('notification_campaigns', 'channel',
                    server_default='all',
                    existing_type=sa.Enum('push', 'email', 'all', name='notificationchannel'))
    op.alter_column('notification_campaigns', 'status',
                    server_default='draft',
                    existing_type=sa.Enum('draft', 'scheduled', 'sent', 'cancelled', name='notificationstatus'))

