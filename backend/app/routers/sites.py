"""
Sites API router - CRUD operations for websites.
"""

import uuid
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.auth import get_current_user, CurrentUser
from app.models import Site, Page, Domain
from app.schemas import (
    SiteResponse, SiteCreateRequest, SiteUpdateRequest,
    PageResponse, SeoSchema, DomainResponse, GlobalSettingsSchema,
)

router = APIRouter(prefix="/sites", tags=["sites"])


def _page_to_response(page: Page) -> PageResponse:
    """Convert Page ORM model to response schema."""
    return PageResponse(
        id=str(page.id),
        siteId=str(page.site_id),
        title=page.title,
        slug=page.slug,
        blocks=[],
        seo=SeoSchema(
            title=page.seo_title or "",
            description=page.seo_description or "",
            keywords=page.seo_keywords,
            ogImage=page.seo_og_image,
            canonicalUrl=page.seo_canonical_url,
            noIndex=page.seo_no_index,
        ),
        status=page.status,
        isMain=page.is_main,
        isHomePage=page.is_home_page,
        createdAt=page.created_at.isoformat() + "Z",
        updatedAt=page.updated_at.isoformat() + "Z",
    )


def _domain_to_response(domain: Domain) -> DomainResponse:
    """Convert Domain ORM model to response schema."""
    return DomainResponse(
        id=str(domain.id),
        siteId=str(domain.site_id),
        domainName=domain.domain_name,
        sslStatus=domain.ssl_status,
        isPrimary=domain.is_primary,
        isVerified=domain.is_verified,
        createdAt=domain.created_at.isoformat() + "Z" if domain.created_at else None,
    )


def _site_to_response(site: Site) -> SiteResponse:
    """Convert Site ORM model to response schema."""
    gs = site.global_settings or {}
    return SiteResponse(
        id=str(site.id),
        userId=site.user_id,
        name=site.name,
        description=site.description,
        subdomain=site.subdomain,
        favicon=site.favicon,
        isPublished=site.is_published,
        globalSettings=GlobalSettingsSchema(**gs) if gs else GlobalSettingsSchema(),
        domains=[_domain_to_response(d) for d in (site.domains or [])],
        pages=[_page_to_response(p) for p in (site.pages or [])],
        status=site.status,
        createdAt=site.created_at.isoformat() + "Z",
        updatedAt=site.updated_at.isoformat() + "Z",
    )


@router.get("", response_model=List[SiteResponse])
async def list_sites(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all sites for the authenticated user."""
    result = await db.execute(
        select(Site)
        .where(Site.user_id == user.user_id)
        .options(selectinload(Site.pages), selectinload(Site.domains))
        .order_by(Site.updated_at.desc())
    )
    sites = result.scalars().all()
    return [_site_to_response(s) for s in sites]


@router.get("/{site_id}", response_model=SiteResponse)
async def get_site(
    site_id: str,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single site by ID."""
    result = await db.execute(
        select(Site)
        .where(Site.id == uuid.UUID(site_id), Site.user_id == user.user_id)
        .options(selectinload(Site.pages), selectinload(Site.domains))
    )
    site = result.scalar_one_or_none()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return _site_to_response(site)


@router.post("", response_model=SiteResponse, status_code=201)
async def create_site(
    data: SiteCreateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new site with a default Home page."""
    site = Site(
        user_id=user.user_id,
        name=data.name,
        description=data.description,
        global_settings={
            "fonts": {"heading": "Inter", "body": "Inter"},
            "colors": {
                "primary": "#1976D2",
                "secondary": "#424242",
                "accent": "#FF5252",
                "background": "#ffffff",
                "text": "#212121",
            },
        },
    )
    db.add(site)
    await db.flush()

    # Create default Home page
    home_page = Page(
        site_id=site.id,
        title="Home",
        slug="/",
        seo_title=f"{data.name} - Home",
        is_main=True,
        is_home_page=True,
    )
    db.add(home_page)
    await db.flush()

    # Reload with relationships
    await db.refresh(site, attribute_names=["pages", "domains"])
    return _site_to_response(site)


@router.patch("/{site_id}", response_model=SiteResponse)
async def update_site(
    site_id: str,
    data: SiteUpdateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Partial update of a site."""
    result = await db.execute(
        select(Site)
        .where(Site.id == uuid.UUID(site_id), Site.user_id == user.user_id)
        .options(selectinload(Site.pages), selectinload(Site.domains))
    )
    site = result.scalar_one_or_none()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    update_data = data.model_dump(exclude_unset=True)
    if "globalSettings" in update_data and update_data["globalSettings"]:
        gs = update_data.pop("globalSettings")
        current_gs = site.global_settings or {}
        current_gs.update(gs)
        site.global_settings = current_gs

    for field, value in update_data.items():
        if field == "name":
            site.name = value
        elif field == "description":
            site.description = value
        elif field == "subdomain":
            site.subdomain = value
        elif field == "favicon":
            site.favicon = value

    site.updated_at = datetime.utcnow()
    await db.flush()
    await db.refresh(site, attribute_names=["pages", "domains"])
    return _site_to_response(site)


@router.delete("/{site_id}", status_code=204)
async def delete_site(
    site_id: str,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a site and all its pages."""
    result = await db.execute(
        select(Site).where(Site.id == uuid.UUID(site_id), Site.user_id == user.user_id)
    )
    site = result.scalar_one_or_none()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    await db.delete(site)


@router.post("/{site_id}/publish")
async def publish_site(
    site_id: str,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Publish a site and all its pages."""
    result = await db.execute(
        select(Site)
        .where(Site.id == uuid.UUID(site_id), Site.user_id == user.user_id)
        .options(selectinload(Site.pages))
    )
    site = result.scalar_one_or_none()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    site.status = "published"
    site.is_published = True
    for page in site.pages:
        page.status = "published"

    site.updated_at = datetime.utcnow()
    await db.flush()

    # TODO: trigger Celery task to generate static HTML
    return {"status": "published"}
