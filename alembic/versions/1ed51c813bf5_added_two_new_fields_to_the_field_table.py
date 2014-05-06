"""Added two new fields to the Field table;

Revision ID: 1ed51c813bf5
Revises: 3f4002121228
Create Date: 2014-05-01 12:40:05.527813

"""

# revision identifiers, used by Alembic.
revision = '1ed51c813bf5'
down_revision = '3f4002121228'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('field', sa.Column('is_public', sa.Boolean))
    op.add_column('field', sa.Column('is_visible', sa.Boolean))


def downgrade():
    pass
