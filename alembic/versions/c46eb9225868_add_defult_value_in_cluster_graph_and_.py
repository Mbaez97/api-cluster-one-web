"""Add defult value in cluster graph and delete unnecesary fields

Revision ID: c46eb9225868
Revises: a8ba78ab268d
Create Date: 2023-09-08 01:35:46.279766

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c46eb9225868'
down_revision = 'a8ba78ab268d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('cluster_graph', sa.Column('p_value', sa.Float(), nullable=False))
    op.create_unique_constraint(None, 'edge', ['protein_a_id', 'protein_b_id', 'direction'])
    op.drop_column('edge', 'weight')
    op.drop_column('edge', 'has_direction')
    op.add_column('edge_cluster_interaction', sa.Column('weight', sa.Float(), nullable=False))
    op.add_column('edge_ppi_interaction', sa.Column('weight', sa.Float(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('edge_ppi_interaction', 'weight')
    op.drop_column('edge_cluster_interaction', 'weight')
    op.add_column('edge', sa.Column('has_direction', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('edge', sa.Column('weight', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'edge', type_='unique')
    op.drop_column('cluster_graph', 'p_value')
    # ### end Alembic commands ###
