"""
Publish task - generates static HTML of published sites.
Runs as a FastAPI BackgroundTask (no Celery required).
"""

import os
import logging
from datetime import datetime

from pymongo import MongoClient
from jinja2 import Environment, FileSystemLoader

from app.core import settings

logger = logging.getLogger(__name__)


def publish_site_task(site_id: str, site_name: str, pages_data: list):
    """
    Generate static HTML for a published site.
    Called as a FastAPI BackgroundTask.

    Args:
        site_id: UUID of the site
        site_name: Name of the site
        pages_data: List of dicts with page_id, title, slug
    """
    logger.info(f"PUBLISH START: site_id={site_id} name='{site_name}' pages={len(pages_data)}")
    try:
        # Connect to MongoDB to get block content
        mongo_client = MongoClient(settings.mongo_url)
        mongo_db = mongo_client[settings.MONGO_DB]
        logger.info(f"PUBLISH: connected to MongoDB")

        # Create publish directory
        site_dir = os.path.join(settings.PUBLISH_DIR, site_id)
        os.makedirs(site_dir, exist_ok=True)
        logger.info(f"PUBLISH: output dir={site_dir}")

        # Setup Jinja2 template
        template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
        if os.path.exists(template_dir):
            env = Environment(loader=FileSystemLoader(template_dir))
            template = env.get_template("published_page.html")
        else:
            template = None

        # Generate HTML for each page
        for page_info in pages_data:
            page_id = page_info["page_id"]
            slug = page_info.get("slug", "/")
            title = page_info.get("title", "Page")
            is_home_page = page_info.get("is_home_page", False)
            html_content = page_info.get("html_content")  # pre-rendered HTML from import

            # Get blocks from MongoDB
            blocks = list(
                mongo_db.blocks.find(
                    {"page_id": page_id},
                    {"_id": 0, "page_id": 0},
                ).sort("order", 1)
            )
            logger.info(f"PUBLISH: page '{title}' (id={page_id}) slug='{slug}' is_home={is_home_page} blocks={len(blocks)} has_html={bool(html_content)}")

            # Generate HTML: prefer pre-rendered html_content (imported sites),
            # then Jinja template with blocks, then fallback
            if html_content:
                html = _sanitize_tilda_html(html_content)
            elif template and blocks:
                html = template.render(
                    title=title,
                    site_name=site_name,
                    blocks=blocks,
                    published_at=datetime.utcnow().isoformat(),
                )
            else:
                html = _generate_fallback_html(title, site_name, blocks)

            # Home page or slug="/" always writes to site root index.html
            if is_home_page or slug == "/":
                filepath = os.path.join(site_dir, "index.html")
            else:
                page_dir = os.path.join(site_dir, slug.strip("/"))
                os.makedirs(page_dir, exist_ok=True)
                filepath = os.path.join(page_dir, "index.html")

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html)

            logger.info(f"Published page '{title}' -> {filepath}")

        mongo_client.close()
        logger.info(f"PUBLISH SUCCESS: site_id={site_id} pages={len(pages_data)} dir={site_dir}")

    except Exception as exc:
        logger.error(f"PUBLISH ERROR: site_id={site_id} error={exc}", exc_info=True)


def _sanitize_tilda_html(html: str) -> str:
    """
    Fix Tilda-specific JS template strings not evaluated in static HTML.

    Tilda uses t_getRootZone() to pick CDN TLD (.com or .info) at runtime.
    In exported/imported HTML these appear as literal concatenation fragments:
      src="https://static.tildacdn.'+t_getRootZone()+'/img/..."
    We replace them with the real '.com' value.
    """
    import re
    # Pattern: '+t_getRootZone()+'  (single-quote JS concatenation)
    html = re.sub(r"'\s*\+\s*t_getRootZone\(\)\s*\+\s*'", '.com', html)
    # Pattern: "+t_getRootZone()+"  (double-quote variant)
    html = re.sub(r'"\s*\+\s*t_getRootZone\(\)\s*\+\s*"', '.com', html)
    # Fallback: bare t_getRootZone() call
    html = html.replace('t_getRootZone()', "'com'")
    return html


def _generate_fallback_html(title: str, site_name: str, blocks: list) -> str:
    """Generate simple HTML when no Jinja template is available."""
    blocks_html = ""
    for block in blocks:
        content = block.get("content", {})
        block_type = block.get("type", "unknown")
        block_title = content.get("title", "")
        block_text = content.get("text", content.get("subtitle", ""))

        blocks_html += f"""
        <section class="block block--{block_type}" style="padding: 40px 20px;">
            {'<h2>' + block_title + '</h2>' if block_title else ''}
            {'<p>' + block_text + '</p>' if block_text else ''}
        </section>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - {site_name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', -apple-system, sans-serif; color: #212121; }}
        h2 {{ margin-bottom: 16px; font-size: 2rem; }}
        p {{ line-height: 1.6; max-width: 700px; margin: 0 auto; }}
        .block {{ text-align: center; }}
    </style>
</head>
<body>
    {blocks_html}
</body>
</html>"""
