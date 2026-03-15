"""make verification code user nullable

Revision ID: 20241114_01
Revises: 2bb956224349
Create Date: 2025-11-14 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20241114_01'
down_revision = '2bb956224349'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        'verification_codes',
        'user_id',
        existing_type=sa.Integer(),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        'verification_codes',
        'user_id',
        existing_type=sa.Integer(),
        nullable=False,
    )


