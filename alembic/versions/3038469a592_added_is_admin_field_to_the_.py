"""Added is_admin field to the UserApplication permissions table;

Revision ID: 3038469a592
Revises: None
Create Date: 2014-04-30 16:55:27.927709

"""

# revision identifiers, used by Alembic.
revision = '3038469a592'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('user_applications', sa.Column('is_admin', sa.Boolean))


def downgrade():
    pass
