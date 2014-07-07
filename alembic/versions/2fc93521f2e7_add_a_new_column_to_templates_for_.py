"""Add a new column to templates for community sharing

Revision ID: 2fc93521f2e7
Revises: 25d12a0d89d1
Create Date: 2014-07-07 10:54:38.618715

"""

# revision identifiers, used by Alembic.
revision = '2fc93521f2e7'
down_revision = '25d12a0d89d1'

from alembic import op
import sqlalchemy as sa


def upgrade():
  op.add_column('template', sa.Column('is_community', sa.Boolean))


def downgrade():
    pass
