"""Added public field to Application table;

Revision ID: 365b1b158fac
Revises: 3f0bab1c21d8
Create Date: 2014-07-22 10:30:29.361375

"""

# revision identifiers, used by Alembic.
revision = '365b1b158fac'
down_revision = '3f0bab1c21d8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('application', sa.Column('is_public', sa.Boolean))


def downgrade():
    pass
