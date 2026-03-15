"""remove_scheduled_at_from_notifications (stub)

Revision ID: b04df0e27bea
Revises: 20241118_01
Create Date: 2025-11-19 19:58:50.805916

Это заглушка для восстановления цепочки миграций.
Фактические изменения перенесены в c32c8d3e066d.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b04df0e27bea'
down_revision: Union[str, None] = '20241118_01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Эта миграция уже применена в базе данных
    # Фактические изменения перенесены в c32c8d3e066d
    pass


def downgrade() -> None:
    pass

