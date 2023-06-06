"""Add data file path for clusters

Revision ID: 91ff7268e1cd
Revises: eb7b5f560892
Create Date: 2023-06-05 02:50:44.739456

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '91ff7268e1cd'
down_revision = 'eb7b5f560892'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('cluster_graph', sa.Column('data', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('cluster_graph', 'data')
    # ### end Alembic commands ###