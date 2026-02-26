"""Add is_imported to sites and html_content to pages.

Revision ID: 002_add_imported_fields
Revises: 001_initial
Create Date: 2026-02-25
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = "002_add_imported_fields"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def _column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column already exists in a table."""
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            "SELECT EXISTS ("
            "  SELECT 1 FROM information_schema.columns "
            "  WHERE table_name = :t AND column_name = :c"
            ")"
        ),
        {"t": table_name, "c": column_name},
    )
    return result.scalar()


def upgrade() -> None:
    # Add is_imported column to sites table
    if not _column_exists("sites", "is_imported"):
        op.add_column(
            "sites",
            sa.Column("is_imported", sa.Boolean, server_default="false", nullable=False),
        )

    # Add html_content column to pages table
    if not _column_exists("pages", "html_content"):
        op.add_column(
            "pages",
            sa.Column("html_content", sa.Text, nullable=True),
        )


def downgrade() -> None:
    op.drop_column("pages", "html_content")
    op.drop_column("sites", "is_imported")
