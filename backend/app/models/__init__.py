"""
SQLAlchemy models for sites and pages (PostgreSQL).
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Text, Boolean, DateTime, Integer,
    ForeignKey, JSON, Enum as SAEnum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Site(Base):
    """Site model - stored in PostgreSQL."""
    __tablename__ = "sites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False, index=True)
    name = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    subdomain = Column(String(100), nullable=True, unique=True)
    favicon = Column(String(1000), nullable=True)
    status = Column(String(20), default="draft", nullable=False)  # draft | published
    is_published = Column(Boolean, default=False)
    is_imported = Column(Boolean, default=False, nullable=False)
    global_settings = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    pages = relationship("Page", back_populates="site", cascade="all, delete-orphan", order_by="Page.created_at")
    domains = relationship("Domain", back_populates="site", cascade="all, delete-orphan")


class Page(Base):
    """Page model - stored in PostgreSQL. Block content is in MongoDB."""
    __tablename__ = "pages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=False)
    slug = Column(String(500), nullable=False, default="/")
    seo_title = Column(String(500), nullable=True)
    seo_description = Column(Text, nullable=True)
    seo_keywords = Column(String(1000), nullable=True)
    seo_og_image = Column(String(1000), nullable=True)
    seo_canonical_url = Column(String(1000), nullable=True)
    seo_no_index = Column(Boolean, default=False)
    status = Column(String(20), default="draft", nullable=False)
    is_main = Column(Boolean, default=False)
    is_home_page = Column(Boolean, default=False)
    html_content = Column(Text, nullable=True)  # Raw HTML for imported pages
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    site = relationship("Site", back_populates="pages")


class Domain(Base):
    """Custom domain model."""
    __tablename__ = "domains"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id", ondelete="CASCADE"), nullable=False)
    domain_name = Column(String(255), nullable=False, unique=True)
    ssl_status = Column(String(20), default="none")  # none | pending | active | error
    is_primary = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    site = relationship("Site", back_populates="domains")
