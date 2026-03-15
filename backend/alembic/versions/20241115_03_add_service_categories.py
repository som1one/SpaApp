"""add service categories and extended service fields

Revision ID: 20241115_03
Revises: 20241115_01
Create Date: 2025-11-15 12:30:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20241115_03"
down_revision: Union[str, None] = "20241115_01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "service_categories",
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["parent_id"], ["service_categories.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_service_categories_id"), "service_categories", ["id"], unique=False)

    op.add_column("services", sa.Column("subtitle", sa.String(length=255), nullable=True))
    op.add_column("services", sa.Column("category_id", sa.Integer(), nullable=True))
    op.add_column("services", sa.Column("detail_image_url", sa.String(length=500), nullable=True))
    op.add_column("services", sa.Column("highlights", sa.JSON(), nullable=True))
    op.add_column("services", sa.Column("contact_link", sa.String(length=500), nullable=True))
    op.add_column("services", sa.Column("contact_label", sa.String(length=100), nullable=True))
    op.add_column("services", sa.Column("book_button_label", sa.String(length=100), nullable=True))
    op.add_column(
        "services",
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
    )

    op.create_foreign_key(
        "fk_services_category",
        "services",
        "service_categories",
        ["category_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # remove server defaults
    op.alter_column("service_categories", "order_index", server_default=None)
    op.alter_column("service_categories", "is_active", server_default=None)
    op.alter_column("services", "order_index", server_default=None)


def downgrade() -> None:
    op.alter_column("services", "order_index", server_default="0")
    op.drop_constraint("fk_services_category", "services", type_="foreignkey")
    op.drop_column("services", "order_index")
    op.drop_column("services", "book_button_label")
    op.drop_column("services", "contact_label")
    op.drop_column("services", "contact_link")
    op.drop_column("services", "highlights")
    op.drop_column("services", "detail_image_url")
    op.drop_column("services", "category_id")
    op.drop_column("services", "subtitle")
    op.drop_index(op.f("ix_service_categories_id"), table_name="service_categories")
    op.drop_table("service_categories")


