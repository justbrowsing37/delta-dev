"""add skill_level to users

Revision ID: 4da3fb106d9f
Revises: d6446c5ba1cd
Create Date: 2026-06-23 09:35:06.768942

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4da3fb106d9f'
down_revision = 'd6446c5ba1cd'
branch_labels = None
depends_on = None


def upgrade():
    # Fix concept_tags cast with explicit USING clause
    op.execute(
        "ALTER TABLE lessons ALTER COLUMN concept_tags TYPE JSON "
        "USING concept_tags::text::json"
    )

    # Add skill_level to users
    op.add_column('users', sa.Column('skill_level', sa.String(20), nullable=True, server_default='beginner'))


def downgrade():
    op.drop_column('users', 'skill_level')

    op.execute(
        "ALTER TABLE lessons ALTER COLUMN concept_tags TYPE VARCHAR(50)[] "
        "USING ARRAY[concept_tags::text]"
    )
