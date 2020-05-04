"""Tabla-imagenes

Revision ID: b26a8d3d0de9
Revises: f3f7bdddb742
Create Date: 2020-05-03 22:38:09.757399

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b26a8d3d0de9'
down_revision = 'f3f7bdddb742'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('idType', sa.String(length=4), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'idType')
    # ### end Alembic commands ###