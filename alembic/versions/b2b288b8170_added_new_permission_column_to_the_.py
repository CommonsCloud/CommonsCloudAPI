"""Added new permission column to the Template table;

Revision ID: b2b288b8170
Revises: 440132f27c9b
Create Date: 2014-10-20 08:58:58.477580

"""

# revision identifiers, used by Alembic.
revision = 'b2b288b8170'
down_revision = '440132f27c9b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('template', sa.Column('has_acl', sa.Boolean))


def downgrade():
    pass
