"""add_loyalty_fields_to_users

Revision ID: 9128530ec343
Revises: ff0b41366a28
Create Date: 2025-11-18 18:08:09.828910

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9128530ec343'
down_revision: Union[str, None] = 'ff0b41366a28'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
