"""Added options column for Fields;

Revision ID: 25d12a0d89d1
Revises: cf086d0211a
Create Date: 2014-06-23 16:06:57.898902

"""

# revision identifiers, used by Alembic.
revision = '25d12a0d89d1'
down_revision = 'cf086d0211a'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('field', sa.Column('options', sa.Text))


def downgrade():
    pass
