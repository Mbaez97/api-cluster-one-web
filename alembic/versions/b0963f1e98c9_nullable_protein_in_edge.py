"""Nullable protein in edge

Revision ID: b0963f1e98c9
Revises: 738a289a1df3
Create Date: 2023-06-04 20:29:05.830537

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b0963f1e98c9"
down_revision = "738a289a1df3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("edge", "protein_a_id", existing_type=sa.INTEGER(), nullable=True)
    op.alter_column("edge", "protein_b_id", existing_type=sa.INTEGER(), nullable=True)
    op.add_column(
        "edge_cluster_interaction",
        sa.Column("cluster_graph_id", sa.Integer(), nullable=True),
    )
    op.drop_constraint(
        "edge_cluster_interaction_ppi_interaction_id_fkey",
        "edge_cluster_interaction",
        type_="foreignkey",
    )
    op.create_foreign_key(
        None, "edge_cluster_interaction", "cluster_graph", ["cluster_graph_id"], ["id"]
    )
    op.drop_column("edge_cluster_interaction", "ppi_interaction_id")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "edge_cluster_interaction",
        sa.Column(
            "ppi_interaction_id", sa.INTEGER(), autoincrement=False, nullable=True
        ),
    )
    op.drop_constraint(None, "edge_cluster_interaction", type_="foreignkey")
    op.create_foreign_key(
        "edge_cluster_interaction_ppi_interaction_id_fkey",
        "edge_cluster_interaction",
        "ppi_graph",
        ["ppi_interaction_id"],
        ["id"],
    )
    op.drop_column("edge_cluster_interaction", "cluster_graph_id")
    op.alter_column("edge", "protein_b_id", existing_type=sa.INTEGER(), nullable=False)
    op.alter_column("edge", "protein_a_id", existing_type=sa.INTEGER(), nullable=False)
    # ### end Alembic commands ###
