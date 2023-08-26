"""Initial migration

Revision ID: b417a058a09a
Revises: 
Create Date: 2023-06-04 05:31:49.383409

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b417a058a09a"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "layout",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("animated", sa.Boolean(), nullable=False),
        sa.Column("node_spacing", sa.Float(), nullable=False),
        sa.Column("randomize", sa.Boolean(), nullable=False),
        sa.Column("max_simulation_time", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_layout_id"), "layout", ["id"], unique=False)
    op.create_table(
        "style",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ccs_styles", sa.JSON(), nullable=False),
        sa.Column("cytoscape_styles", sa.JSON(), nullable=False),
        sa.Column("type", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_style_id"), "style", ["id"], unique=False)
    op.create_table(
        "graph",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("size", sa.Integer(), nullable=False),
        sa.Column("density", sa.Float(), nullable=False),
        sa.Column("layout_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["layout_id"],
            ["layout.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_graph_id"), "graph", ["id"], unique=False)
    op.create_table(
        "protein",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("url_info", sa.String(length=255), nullable=True),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("style_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["style_id"],
            ["style.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_protein_id"), "protein", ["id"], unique=False)
    op.create_table(
        "protein_complex",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("url_info", sa.String(length=255), nullable=True),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("style_id", sa.Integer(), nullable=False),
        sa.Column("is_important", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["style_id"],
            ["style.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_protein_complex_id"), "protein_complex", ["id"], unique=False
    )
    op.create_table(
        "cluster_graph",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("quality", sa.Float(), nullable=False),
        sa.Column("external_weight", sa.Float(), nullable=False),
        sa.Column("internal_weight", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(
            ["id"],
            ["graph.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_cluster_graph_id"), "cluster_graph", ["id"], unique=False)
    op.create_table(
        "edge",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("protein_a_id", sa.Integer(), nullable=False),
        sa.Column("protein_b_id", sa.Integer(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("has_direction", sa.Boolean(), nullable=False),
        sa.Column("direction", sa.Integer(), nullable=False),
        sa.Column("style_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["protein_a_id"],
            ["protein.id"],
        ),
        sa.ForeignKeyConstraint(
            ["protein_b_id"],
            ["protein.id"],
        ),
        sa.ForeignKeyConstraint(
            ["style_id"],
            ["style.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_edge_id"), "edge", ["id"], unique=False)
    op.create_table(
        "ppi_graph",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("preloaded", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["id"],
            ["graph.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ppi_graph_id"), "ppi_graph", ["id"], unique=False)
    op.create_table(
        "complex_cluster_one_interaction",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cluster_id", sa.Integer(), nullable=True),
        sa.Column("complex_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["cluster_id"],
            ["cluster_graph.id"],
        ),
        sa.ForeignKeyConstraint(
            ["complex_id"],
            ["protein_complex.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_complex_cluster_one_interaction_id"),
        "complex_cluster_one_interaction",
        ["id"],
        unique=False,
    )
    op.create_table(
        "edge_cluster_interaction",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("edge_id", sa.Integer(), nullable=True),
        sa.Column("ppi_interaction_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["edge_id"],
            ["edge.id"],
        ),
        sa.ForeignKeyConstraint(
            ["ppi_interaction_id"],
            ["ppi_graph.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_edge_cluster_interaction_id"),
        "edge_cluster_interaction",
        ["id"],
        unique=False,
    )
    op.create_table(
        "edge_ppi_interaction",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("edge_id", sa.Integer(), nullable=True),
        sa.Column("ppi_interaction_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["edge_id"],
            ["edge.id"],
        ),
        sa.ForeignKeyConstraint(
            ["ppi_interaction_id"],
            ["ppi_graph.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_edge_ppi_interaction_id"), "edge_ppi_interaction", ["id"], unique=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_edge_ppi_interaction_id"), table_name="edge_ppi_interaction")
    op.drop_table("edge_ppi_interaction")
    op.drop_index(
        op.f("ix_edge_cluster_interaction_id"), table_name="edge_cluster_interaction"
    )
    op.drop_table("edge_cluster_interaction")
    op.drop_index(
        op.f("ix_complex_cluster_one_interaction_id"),
        table_name="complex_cluster_one_interaction",
    )
    op.drop_table("complex_cluster_one_interaction")
    op.drop_index(op.f("ix_ppi_graph_id"), table_name="ppi_graph")
    op.drop_table("ppi_graph")
    op.drop_index(op.f("ix_edge_id"), table_name="edge")
    op.drop_table("edge")
    op.drop_index(op.f("ix_cluster_graph_id"), table_name="cluster_graph")
    op.drop_table("cluster_graph")
    op.drop_index(op.f("ix_protein_complex_id"), table_name="protein_complex")
    op.drop_table("protein_complex")
    op.drop_index(op.f("ix_protein_id"), table_name="protein")
    op.drop_table("protein")
    op.drop_index(op.f("ix_graph_id"), table_name="graph")
    op.drop_table("graph")
    op.drop_index(op.f("ix_style_id"), table_name="style")
    op.drop_table("style")
    op.drop_index(op.f("ix_layout_id"), table_name="layout")
    op.drop_table("layout")
    # ### end Alembic commands ###
