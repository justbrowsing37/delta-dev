"""Add curriculum item metadata for lessons and activities

Revision ID: f4d2ed5e1a2b
Revises: d6446c5ba1cd
Create Date: 2026-06-28 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f4d2ed5e1a2b'
down_revision = 'd6446c5ba1cd'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('lessons', schema=None) as batch_op:
        batch_op.add_column(sa.Column('item_type', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('connects_to', sa.JSON(), nullable=True))


def downgrade():
    with op.batch_alter_table('lessons', schema=None) as batch_op:
        batch_op.drop_column('connects_to')
        batch_op.drop_column('item_type')
