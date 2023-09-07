"""Delete style for everithing

Revision ID: f754a8d7a4e0
Revises: f875dbcdfeeb
Create Date: 2023-09-07 02:19:46.011024

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f754a8d7a4e0'
down_revision = 'f875dbcdfeeb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('protein_style_id_fkey', 'protein', type_='foreignkey')
    op.drop_column('protein', 'style_id')
    op.drop_constraint('protein_complex_style_id_fkey', 'protein_complex', type_='foreignkey')
    op.drop_column('protein_complex', 'style_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('protein_complex', sa.Column('style_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('protein_complex_style_id_fkey', 'protein_complex', 'style', ['style_id'], ['id'])
    op.add_column('protein', sa.Column('style_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('protein_style_id_fkey', 'protein', 'style', ['style_id'], ['id'])
    # ### end Alembic commands ###