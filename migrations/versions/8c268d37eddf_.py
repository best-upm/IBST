"""empty message

Revision ID: 8c268d37eddf
Revises: 7b90b8c05dcd
Create Date: 2020-02-08 19:00:57.445659

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c268d37eddf'
down_revision = '7b90b8c05dcd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('Escuela', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'Escuela')
    # ### end Alembic commands ###
