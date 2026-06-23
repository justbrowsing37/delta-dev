"""add skill_level to users

Revision ID: 4da3fb106d9f
Revises: d6446c5ba1cd
Create Date: 2026-06-23 09:35:06.768942

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "4da3fb106d9f"
down_revision = "d6446c5ba1cd"
branch_labels = None
depends_on = None


def upgrade():
    # ### adjusted migration: ensure array -> json conversion using to_json() ###
    # Use raw SQL to control the USING clause so Postgres can convert the array to JSON safely.
    op.execute("""
    ALTER TABLE lessons
    ALTER COLUMN concept_tags TYPE JSON
    USING to_json(concept_tags);
    """)


def downgrade():
    # ### adjusted migration: convert json -> varchar(50)[] using json_array_elements_text ###
    # This will turn a JSON array of strings back into a Postgres text array, then cast to varchar(50)[]
    op.execute("""
    ALTER TABLE lessons
    ALTER COLUMN concept_tags TYPE varchar(50)[]
    USING (array(SELECT json_array_elements_text(concept_tags)));
    """)

    # ### end adjustments ###
