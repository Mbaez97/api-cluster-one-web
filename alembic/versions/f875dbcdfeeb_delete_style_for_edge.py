"""Delete style for edge

Revision ID: f875dbcdfeeb
Revises: a393d6521a38
Create Date: 2023-09-07 02:08:02.509346

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f875dbcdfeeb"
down_revision = "a393d6521a38"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("edge_style_id_fkey", "edge", type_="foreignkey")
    op.drop_column("edge", "style_id")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "edge", sa.Column("style_id", sa.INTEGER(), autoincrement=False, nullable=False)
    )
    op.create_foreign_key("edge_style_id_fkey", "edge", "style", ["style_id"], ["id"])
    # ### end Alembic commands ###
