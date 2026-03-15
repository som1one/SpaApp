"""add success/failure stats to notification campaigns

Revision ID: 20241115_07
Revises: 20241115_06
Create Date: 2025-11-15 16:40:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20241115_07"
down_revision: Union[str, None] = "20241115_06"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("notification_campaigns", sa.Column("success_count", sa.Integer(), nullable=True))
    op.add_column("notification_campaigns", sa.Column("failure_count", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("notification_campaigns", "failure_count")
    op.drop_column("notification_campaigns", "success_count")


