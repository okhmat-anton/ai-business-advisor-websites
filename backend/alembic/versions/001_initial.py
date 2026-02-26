"""Initial migration - create sites, pages, domains tables.

Revision ID: 001_initial
Revises: -
Create Date: 2026-02-25
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def _table_exists(table_name: str) -> bool:
    """Check if a table already exists in the database."""
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = :t)"
        ),
        {"t": table_name},
    )
    return result.scalar()


def upgrade() -> None:
    # Sites table
    if not _table_exists("sites"):
        op.create_table(
            "sites",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("user_id", sa.String(255), nullable=False, index=True),
            sa.Column("name", sa.String(500), nullable=False),
            sa.Column("description", sa.Text, nullable=True),
            sa.Column("subdomain", sa.String(100), nullable=True, unique=True),
            sa.Column("favicon", sa.String(1000), nullable=True),
            sa.Column("status", sa.String(20), server_default="draft", nullable=False),
            sa.Column("is_published", sa.Boolean, server_default="false"),
            sa.Column("global_settings", sa.JSON, server_default="{}"),
            sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        )

    # Pages table
    if not _table_exists("pages"):
        op.create_table(
            "pages",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column(
                "site_id",
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("sites.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("title", sa.String(500), nullable=False),
            sa.Column("slug", sa.String(500), nullable=False, server_default="/"),
            sa.Column("seo_title", sa.String(500), nullable=True),
            sa.Column("seo_description", sa.Text, nullable=True),
            sa.Column("seo_keywords", sa.String(1000), nullable=True),
            sa.Column("seo_og_image", sa.String(1000), nullable=True),
            sa.Column("seo_canonical_url", sa.String(1000), nullable=True),
            sa.Column("seo_no_index", sa.Boolean, server_default="false"),
            sa.Column("status", sa.String(20), server_default="draft", nullable=False),
            sa.Column("is_main", sa.Boolean, server_default="false"),
            sa.Column("is_home_page", sa.Boolean, server_default="false"),
            sa.Column("sort_order", sa.Integer, server_default="0"),
            sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        )

    # Domains table
    if not _table_exists("domains"):
        op.create_table(
            "domains",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column(
                "site_id",
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("sites.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("domain_name", sa.String(255), nullable=False, unique=True),
            sa.Column("ssl_status", sa.String(20), server_default="none"),
            sa.Column("is_primary", sa.Boolean, server_default="false"),
            sa.Column("is_verified", sa.Boolean, server_default="false"),
            sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        )


def downgrade() -> None:
    op.drop_table("domains")
    op.drop_table("pages")
    op.drop_table("sites")
