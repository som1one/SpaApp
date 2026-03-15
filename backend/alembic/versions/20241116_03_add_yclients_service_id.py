"""Add yclients_service_id to services

Revision ID: 20241116_03
Revises: 20241116_02
Create Date: 2024-11-16
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20241116_03"
down_revision: Union[str, None] = "20241116_02"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('services', sa.Column('yclients_service_id', sa.Integer(), nullable=True))
    op.add_column('services', sa.Column('yclients_staff_id', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('services', 'yclients_staff_id')
    op.drop_column('services', 'yclients_service_id')

