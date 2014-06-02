"""Update name of Notification relationship field on Conditions and Actions;

Revision ID: cf086d0211a
Revises: 17350373a143
Create Date: 2014-06-01 10:56:21.323915

"""

# revision identifiers, used by Alembic.
revision = 'cf086d0211a'
down_revision = '17350373a143'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('action', 'notification', new_column_name='notification_id')
    op.alter_column('condition', 'notification', new_column_name='notification_id')
