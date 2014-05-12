"""Adding Caption, Credit, and Credit Link fields to all Attachment tables;

Revision ID: 17350373a143
Revises: 1ed51c813bf5
Create Date: 2014-05-12 11:04:50.972625

"""

# revision identifiers, used by Alembic.
revision = '17350373a143'
down_revision = '1ed51c813bf5'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('attachment_2e80581e6df343088e5ddd4de30c7955', sa.Column('caption', sa.String(255)))
    op.add_column('attachment_2e80581e6df343088e5ddd4de30c7955', sa.Column('credit', sa.String(255)))
    op.add_column('attachment_2e80581e6df343088e5ddd4de30c7955', sa.Column('credit_link', sa.String(255)))

    op.add_column('attachment_67bf2aa7f8c04d9da3287b393dadfa0b', sa.Column('caption', sa.String(255)))
    op.add_column('attachment_67bf2aa7f8c04d9da3287b393dadfa0b', sa.Column('credit', sa.String(255)))
    op.add_column('attachment_67bf2aa7f8c04d9da3287b393dadfa0b', sa.Column('credit_link', sa.String(255)))

    op.add_column('attachment_fe6eb391238a42d78249c692e9796cf2', sa.Column('caption', sa.String(255)))
    op.add_column('attachment_fe6eb391238a42d78249c692e9796cf2', sa.Column('credit', sa.String(255)))
    op.add_column('attachment_fe6eb391238a42d78249c692e9796cf2', sa.Column('credit_link', sa.String(255)))

def downgrade():
    pass
