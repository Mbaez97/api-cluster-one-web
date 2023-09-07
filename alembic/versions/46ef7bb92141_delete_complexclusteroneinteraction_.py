"""Delete ComplexClusterOneInteraction model

Revision ID: 46ef7bb92141
Revises: 22133c0c5623
Create Date: 2023-09-07 06:46:10.284728

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "46ef7bb92141"
down_revision = "22133c0c5623"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        "ix_complex_cluster_one_interaction_id",
        table_name="complex_cluster_one_interaction",
    )
    op.drop_table("complex_cluster_one_interaction")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "complex_cluster_one_interaction",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("cluster_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("complex_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column(
            "created_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "updated_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "deleted_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["cluster_id"],
            ["cluster_graph.id"],
            name="complex_cluster_one_interaction_cluster_id_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["complex_id"],
            ["protein_complex.id"],
            name="complex_cluster_one_interaction_complex_id_fkey",
        ),
        sa.PrimaryKeyConstraint("id", name="complex_cluster_one_interaction_pkey"),
    )
    op.create_index(
        "ix_complex_cluster_one_interaction_id",
        "complex_cluster_one_interaction",
        ["id"],
        unique=False,
    )
    # ### end Alembic commands ###
