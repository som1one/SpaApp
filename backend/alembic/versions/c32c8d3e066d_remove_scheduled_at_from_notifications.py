"""remove_scheduled_at_from_notifications

Revision ID: c32c8d3e066d
Revises: b04df0e27bea
Create Date: 2025-11-19 20:15:31.259725

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c32c8d3e066d'
down_revision: Union[str, None] = 'b04df0e27bea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Обновляем статус: меняем все "scheduled" на "draft"
    # (колонка status уже VARCHAR после предыдущей миграции)
    op.execute("""
        UPDATE notification_campaigns 
        SET status = 'draft' 
        WHERE status = 'scheduled'
    """)
    
    # Удаляем колонку scheduled_at
    op.drop_column("notification_campaigns", "scheduled_at")


def downgrade() -> None:
    # Восстанавливаем колонку scheduled_at
    op.add_column(
        "notification_campaigns",
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
    )
