"""
Pages API router - CRUD operations for site pages.
"""

import uuid
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user, CurrentUser
from app.models import Site, Page
from app.schemas import PageResponse, PageCreateRequest, PageUpdateRequest, SeoSchema

router = APIRouter(prefix="/sites/{site_id}/pages", tags=["pages"])


def _slugify(text: str) -> str:
    """Simple slugify for page URLs."""
    import re
    slug = text.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    return slug.strip('-')


def _page_to_response(page: Page) -> PageResponse:
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


async def _get_user_site(site_id: str, user: CurrentUser, db: AsyncSession) -> Site:
    """Helper to get and verify site ownership."""
    result = await db.execute(
        select(Site).where(Site.id == uuid.UUID(site_id), Site.user_id == user.user_id)
    )
    site = result.scalar_one_or_none()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site


@router.post("", response_model=PageResponse, status_code=201)
async def create_page(
    site_id: str,
    data: PageCreateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new page in a site."""
    await _get_user_site(site_id, user, db)

    slug = data.slug or _slugify(data.title)
    page = Page(
        site_id=uuid.UUID(site_id),
        title=data.title,
        slug=slug,
        seo_title=data.title,
    )
    db.add(page)
    await db.flush()
    return _page_to_response(page)


@router.patch("/{page_id}", response_model=PageResponse)
async def update_page(
    site_id: str,
    page_id: str,
    data: PageUpdateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Partial update of a page."""
    await _get_user_site(site_id, user, db)

    result = await db.execute(
        select(Page).where(
            Page.id == uuid.UUID(page_id),
            Page.site_id == uuid.UUID(site_id),
        )
    )
    page = result.scalar_one_or_none()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    update_data = data.model_dump(exclude_unset=True)

    if "title" in update_data:
        page.title = update_data["title"]
    if "slug" in update_data:
        page.slug = update_data["slug"]
    if "status" in update_data:
        page.status = update_data["status"]
    if "isMain" in update_data:
        page.is_main = update_data["isMain"]
    if "isHomePage" in update_data:
        page.is_home_page = update_data["isHomePage"]
    if "seo" in update_data and update_data["seo"]:
        seo = update_data["seo"]
        page.seo_title = seo.get("title", page.seo_title)
        page.seo_description = seo.get("description", page.seo_description)
        page.seo_keywords = seo.get("keywords", page.seo_keywords)
        page.seo_og_image = seo.get("ogImage", page.seo_og_image)
        page.seo_canonical_url = seo.get("canonicalUrl", page.seo_canonical_url)
        page.seo_no_index = seo.get("noIndex", page.seo_no_index)

    page.updated_at = datetime.utcnow()
    await db.flush()
    return _page_to_response(page)


@router.delete("/{page_id}", status_code=204)
async def delete_page(
    site_id: str,
    page_id: str,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a page."""
    await _get_user_site(site_id, user, db)

    result = await db.execute(
        select(Page).where(
            Page.id == uuid.UUID(page_id),
            Page.site_id == uuid.UUID(site_id),
        )
    )
    page = result.scalar_one_or_none()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    await db.delete(page)


@router.post("/{page_id}/publish")
async def publish_page(
    site_id: str,
    page_id: str,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Publish a single page."""
    await _get_user_site(site_id, user, db)

    result = await db.execute(
        select(Page).where(
            Page.id == uuid.UUID(page_id),
            Page.site_id == uuid.UUID(site_id),
        )
    )
    page = result.scalar_one_or_none()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    page.status = "published"
    page.updated_at = datetime.utcnow()
    await db.flush()

    return {"status": "published"}
