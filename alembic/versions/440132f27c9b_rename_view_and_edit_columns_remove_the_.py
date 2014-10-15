"""Rename view and edit columns; Remove the is_moderator column from the UserApplications table;

Revision ID: 440132f27c9b
Revises: 31f290aad01c
Create Date: 2014-10-15 08:35:48.417283

"""

# revision identifiers, used by Alembic.
revision = '440132f27c9b'
down_revision = '31f290aad01c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('user_applications', 'view', new_column_name='read')
    op.alter_column('user_applications', 'edit', new_column_name='write')
    op.drop_column('user_applications', 'is_moderator')


def downgrade():
    pass
