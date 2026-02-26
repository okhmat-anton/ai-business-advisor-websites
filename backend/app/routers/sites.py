"""
Sites API router - CRUD operations for websites.
"""

import uuid
import os
import socket
import asyncio
import subprocess
import logging
from datetime import datetime
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.auth import get_current_user, CurrentUser
from app.core import settings
from app.models import Site, Page, Domain
from app.schemas import (
    SiteResponse, SiteCreateRequest, SiteUpdateRequest,
    PageResponse, SeoSchema, DomainResponse, DomainCreateRequest,
    DomainVerifyResponse, GlobalSettingsSchema,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sites", tags=["sites"])


def _page_to_response(page: Page) -> PageResponse:
    """Convert Page ORM model to response schema."""
    return PageResponse(
        id=str(page.id),
        siteId=str(page.site_id),
        title=page.title,
        slug=page.slug,
        blocks=[],
        htmlContent=page.html_content,
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
        isImported=site.is_imported,
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
        is_imported=data.is_imported or False,
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
    background_tasks: BackgroundTasks,
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

    # Enqueue static HTML generation as a background task (no Celery needed)
    pages_data = [
        {
            "page_id": str(page.id),
            "title": page.title,
            "slug": page.slug or "/",
        }
        for page in site.pages
    ]
    from app.tasks.publish import publish_site_task
    background_tasks.add_task(publish_site_task, str(site.id), site.name, pages_data)
    logger.info(
        f"PUBLISH TRIGGERED: site_id={site.id} name='{site.name}' "
        f"pages={len(pages_data)} user={user.user_id}"
    )

    return {"status": "published"}


# ========== Domain Management ==========

async def _get_site_for_user(
    site_id: str, user: CurrentUser, db: AsyncSession
) -> Site:
    """Helper: load site owned by user or raise 404."""
    result = await db.execute(
        select(Site)
        .where(Site.id == uuid.UUID(site_id), Site.user_id == user.user_id)
        .options(selectinload(Site.pages), selectinload(Site.domains))
    )
    site = result.scalar_one_or_none()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site


@router.get("/{site_id}/domains", response_model=List[DomainResponse])
async def list_domains(
    site_id: str,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all domains for a site."""
    site = await _get_site_for_user(site_id, user, db)
    return [_domain_to_response(d) for d in site.domains]


@router.post("/{site_id}/domains", response_model=DomainResponse, status_code=201)
async def add_domain(
    site_id: str,
    data: DomainCreateRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a custom domain to a site."""
    site = await _get_site_for_user(site_id, user, db)

    # Normalize domain name
    domain_name = data.domainName.strip().lower()
    if domain_name.startswith("http://") or domain_name.startswith("https://"):
        domain_name = domain_name.split("://", 1)[1]
    domain_name = domain_name.rstrip("/")

    # Check uniqueness
    existing = await db.execute(
        select(Domain).where(Domain.domain_name == domain_name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail=f"Domain '{domain_name}' is already registered",
        )

    domain = Domain(
        site_id=site.id,
        domain_name=domain_name,
        is_primary=data.isPrimary or False,
    )
    db.add(domain)
    await db.flush()
    await db.refresh(domain)
    return _domain_to_response(domain)


@router.delete("/{site_id}/domains/{domain_id}", status_code=204)
async def remove_domain(
    site_id: str,
    domain_id: str,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a custom domain from a site."""
    site = await _get_site_for_user(site_id, user, db)
    result = await db.execute(
        select(Domain).where(
            Domain.id == uuid.UUID(domain_id),
            Domain.site_id == site.id,
        )
    )
    domain = result.scalar_one_or_none()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    await db.delete(domain)


@router.post("/{site_id}/domains/{domain_id}/verify", response_model=DomainVerifyResponse)
async def verify_domain(
    site_id: str,
    domain_id: str,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Verify that a domain's A record points to our server IP."""
    site = await _get_site_for_user(site_id, user, db)
    result = await db.execute(
        select(Domain).where(
            Domain.id == uuid.UUID(domain_id),
            Domain.site_id == site.id,
        )
    )
    domain = result.scalar_one_or_none()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")

    from app.core.ip_detect import get_server_ip
    expected_ip = await get_server_ip()
    if not expected_ip:
        raise HTTPException(
            status_code=500,
            detail="Could not determine server IP. Set SERVER_IP in .env.",
        )

    # Resolve domain DNS in a thread to avoid blocking
    loop = asyncio.get_event_loop()
    try:
        resolved_ips = await loop.run_in_executor(
            None,
            lambda: [r[4][0] for r in socket.getaddrinfo(domain.domain_name, None, socket.AF_INET)],
        )
        resolved_ips = list(set(resolved_ips))  # deduplicate
    except socket.gaierror:
        resolved_ips = []

    is_verified = expected_ip in resolved_ips

    # Update DB
    domain.is_verified = is_verified
    await db.flush()

    if is_verified:
        message = f"Domain '{domain.domain_name}' is correctly pointing to {expected_ip}"
    elif resolved_ips:
        message = (
            f"Domain '{domain.domain_name}' points to {', '.join(resolved_ips)}, "
            f"but expected {expected_ip}. Update your A record."
        )
    else:
        message = (
            f"Could not resolve '{domain.domain_name}'. "
            f"Add an A record pointing to {expected_ip}."
        )

    return DomainVerifyResponse(
        isVerified=is_verified,
        domainName=domain.domain_name,
        resolvedIps=resolved_ips,
        expectedIp=expected_ip,
        message=message,
    )


@router.post("/{site_id}/domains/{domain_id}/ssl")
async def enable_ssl(
    site_id: str,
    domain_id: str,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Request SSL certificate via certbot for a verified domain."""
    site = await _get_site_for_user(site_id, user, db)
    result = await db.execute(
        select(Domain).where(
            Domain.id == uuid.UUID(domain_id),
            Domain.site_id == site.id,
        )
    )
    domain = result.scalar_one_or_none()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")

    if not domain.is_verified:
        raise HTTPException(
            status_code=400,
            detail="Domain must be verified before enabling SSL. Run verification first.",
        )

    if domain.ssl_status == "active":
        # Regenerate nginx config (in case template changed) and reload
        await _setup_nginx_ssl(domain.domain_name, str(site.id))
        return {"status": "active", "message": "SSL is already active for this domain. Nginx config regenerated."}

    # Mark as pending
    domain.ssl_status = "pending"
    await db.flush()

    # Run certbot in a subprocess
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(None, _run_certbot, domain.domain_name)
        if result["success"]:
            # Generate nginx SSL config for published site and reload nginx
            await _setup_nginx_ssl(domain.domain_name, str(site.id))
            domain.ssl_status = "active"
            await db.flush()
            return {
                "status": "active",
                "message": f"SSL certificate obtained for {domain.domain_name}",
            }
        else:
            domain.ssl_status = "error"
            await db.flush()
            logger.error(f"Certbot failed for {domain.domain_name}: {result['error']}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to obtain SSL certificate: {result['error']}",
            )
    except Exception as e:
        domain.ssl_status = "error"
        await db.flush()
        logger.error(f"SSL error for {domain.domain_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"SSL certificate request failed: {str(e)}",
        )


def _run_certbot(domain_name: str) -> dict:
    """Run certbot to obtain an SSL certificate. Runs in a thread."""
    import shutil

    certbot_path = shutil.which("certbot")
    logger.info(f"SSL: Starting certbot for {domain_name}, certbot_path={certbot_path}")

    if not certbot_path:
        logger.error("SSL: certbot binary not found in PATH")
        return {"success": False, "error": "certbot is not installed on the server"}

    try:
        cmd = [
            "certbot", "certonly",
            "--webroot",
            "-w", "/var/www/acme",
            "--config-dir", "/etc/custom-ssl",
            "--work-dir", "/tmp/certbot-work",
            "--logs-dir", "/tmp/certbot-logs",
            "-d", domain_name,
            "--non-interactive",
            "--agree-tos",
            "--email", "admin@akm-advisor.com",
            "--no-eff-email",
        ]
        logger.info(f"SSL: Running command: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        logger.info(f"SSL: certbot exit code={result.returncode}")
        if result.stdout:
            logger.info(f"SSL: certbot stdout: {result.stdout}")
        if result.stderr:
            logger.info(f"SSL: certbot stderr: {result.stderr}")

        if result.returncode == 0:
            return {"success": True}
        else:
            return {"success": False, "error": result.stderr or result.stdout}
    except FileNotFoundError:
        logger.error("SSL: certbot FileNotFoundError")
        return {"success": False, "error": "certbot is not installed on the server"}
    except subprocess.TimeoutExpired:
        logger.error("SSL: certbot timed out after 120s")
        return {"success": False, "error": "certbot timed out (120s)"}
    except Exception as e:
        logger.error(f"SSL: certbot unexpected error: {e}")
        return {"success": False, "error": str(e)}


# Directory for generated nginx SSL configs (shared volume with nginx)
NGINX_SSL_CONF_DIR = "/etc/nginx/ssl-sites"


async def _setup_nginx_ssl(domain_name: str, site_id: str):
    """Generate nginx SSL server block for a custom domain serving published site content."""
    os.makedirs(NGINX_SSL_CONF_DIR, exist_ok=True)

    conf_content = f"""# Auto-generated SSL config for {domain_name}
# Serves published site content for site_id: {site_id}
server {{
    listen 443 ssl;
    server_name {domain_name};

    ssl_certificate /etc/custom-ssl/live/{domain_name}/fullchain.pem;
    ssl_certificate_key /etc/custom-ssl/live/{domain_name}/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Published site content (root of the custom domain)
    root /app/published/{site_id};
    index index.html;

    location / {{
        try_files $uri $uri/ =404;
    }}

    # Proxy to API backend (for forms, analytics, etc.)
    location /api/ {{
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_read_timeout 120s;
    }}

    # Uploaded files (images, media used by the published site)
    location /uploads/ {{
        alias /app/uploads/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }}

    # Static assets caching
    location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot|webp)$ {{
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
}}

# HTTP -> HTTPS redirect for {domain_name}
server {{
    listen 80;
    server_name {domain_name};

    location /.well-known/acme-challenge/ {{
        root /var/www/acme;
        try_files $uri =404;
    }}

    location / {{
        return 301 https://$host$request_uri;
    }}
}}
"""
    conf_path = os.path.join(NGINX_SSL_CONF_DIR, f"{domain_name}.conf")
    with open(conf_path, "w") as f:
        f.write(conf_content)
    logger.info(f"SSL: Wrote nginx config to {conf_path}")

    # Reload nginx container via docker socket
    await _reload_nginx()


async def _reload_nginx():
    """Reload nginx by sending HUP signal via docker socket API."""
    docker_sock = "/var/run/docker.sock"
    if not os.path.exists(docker_sock):
        logger.warning("SSL: docker.sock not available, cannot reload nginx")
        return

    try:
        # Send SIGHUP to nginx container to reload config
        proc = await asyncio.create_subprocess_exec(
            "curl", "-s", "-X", "POST",
            "--unix-socket", docker_sock,
            "http://localhost/containers/sb-nginx/kill?signal=HUP",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=10)
        logger.info(f"SSL: Nginx reload signal sent (exit={proc.returncode})")
    except Exception as e:
        logger.error(f"SSL: Failed to reload nginx: {e}")
