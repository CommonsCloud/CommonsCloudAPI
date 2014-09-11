"""Add new notify column to Activity

Revision ID: 31f290aad01c
Revises: 365b1b158fac
Create Date: 2014-09-11 12:03:08.648105

"""

# revision identifiers, used by Alembic.
revision = '31f290aad01c'
down_revision = '365b1b158fac'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('activity', sa.Column('notify', sa.Text))


def downgrade():
    pass
