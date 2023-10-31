"""Add mil cosas que capaz antes no se aplico

Revision ID: 9ff110700fee
Revises: 735f89b1efdc
Create Date: 2023-10-27 05:34:58.404572

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9ff110700fee"
down_revision = "735f89b1efdc"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###

    op.create_table(
        "go_terms",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("term", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("url_info", sa.String(length=255), nullable=True),
        sa.Column("domain", sa.String(length=2), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_go_terms_id"), "go_terms", ["id"], unique=False)
    # ### end Alembic commands ###
    op.create_table(
        "enrichment",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("p_value", sa.Float(), nullable=False),
        sa.Column("is_important", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("go_terms_id", sa.Integer(), nullable=False),
        sa.Column("cluster_graph_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["cluster_graph_id"],
            ["cluster_graph.id"],
        ),
        sa.ForeignKeyConstraint(
            ["go_terms_id"],
            ["go_terms.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_enrichment_id"), "enrichment", ["id"], unique=False)

    op.add_column(
        "cluster_graph", sa.Column("enrichment_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        None, "cluster_graph", "enrichment", ["enrichment_id"], ["id"]
    )


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "cluster_graph", type_="foreignkey")
    op.drop_column("cluster_graph", "enrichment_id")
    op.drop_index(op.f("ix_go_terms_id"), table_name="go_terms")
    op.drop_table("go_terms")
    op.drop_index(op.f("ix_enrichment_id"), table_name="enrichment")
    op.drop_table("enrichment")
    # ### end Alembic commands ###