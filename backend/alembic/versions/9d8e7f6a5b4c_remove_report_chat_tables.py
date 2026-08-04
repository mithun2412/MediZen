"""Remove unused report chat and report parameter tables.

Revision ID: 9d8e7f6a5b4c
Revises: 7a4ea6c0f091
"""

from alembic import op


revision = "9d8e7f6a5b4c"
down_revision = "7a4ea6c0f091"
branch_labels = None
depends_on = None


def upgrade():
    """Delete unused report feature tables and their stored data."""
    op.execute("DROP TABLE IF EXISTS report_chats CASCADE")
    op.execute("DROP TABLE IF EXISTS report_parameters CASCADE")


def downgrade():
    """The removed report chat and parameter data cannot be restored."""
    pass
