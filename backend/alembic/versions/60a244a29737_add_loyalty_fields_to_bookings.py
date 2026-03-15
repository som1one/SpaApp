"""add_loyalty_fields_to_bookings

Revision ID: 60a244a29737
Revises: 20241220_01
Create Date: 2025-11-21 16:45:31.293183

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '60a244a29737'
down_revision: Union[str, None] = '20241220_01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Эта миграция пустая, так как поля уже добавлены в миграции 20241220_01
    pass


def downgrade() -> None:
    # Эта миграция пустая, так как поля уже добавлены в миграции 20241220_01
    pass
