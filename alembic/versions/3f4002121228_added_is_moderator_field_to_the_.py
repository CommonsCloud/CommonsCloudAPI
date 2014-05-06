"""Added is_moderator field to the UserApplication permissions table;

Revision ID: 3f4002121228
Revises: 3038469a592
Create Date: 2014-04-30 16:59:02.700158

"""

# revision identifiers, used by Alembic.
revision = '3f4002121228'
down_revision = '3038469a592'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('user_applications', sa.Column('is_moderator', sa.Boolean))


def downgrade():
    pass
