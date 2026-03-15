"""merge staff desc branch

Revision ID: 653b009841e0
Revises: add_staff_desc, 20250110_01
Create Date: 2025-11-22 11:36:37.587605

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '653b009841e0'
down_revision: Union[str, None] = ('add_staff_desc', '20250110_01')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
