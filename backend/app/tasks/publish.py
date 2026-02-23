"""
Publish task - generates static HTML of published sites.
"""

import os
import json
from datetime import datetime

from pymongo import MongoClient
from jinja2 import Environment, FileSystemLoader

from app.celery_app import celery_app
from app.core import settings


@celery_app.task(bind=True, max_retries=3)
def publish_site_task(self, site_id: str, site_name: str, pages_data: list):
    """
    Generate static HTML for a published site.

    Args:
        site_id: UUID of the site
        site_name: Name of the site (used for directory)
        pages_data: List of dicts with page_id, title, slug
    """
    try:
        # Connect to MongoDB to get block content
        mongo_client = MongoClient(settings.mongo_url)
        mongo_db = mongo_client[settings.MONGO_DB]

        # Create publish directory
        site_dir = os.path.join(settings.PUBLISH_DIR, site_id)
        os.makedirs(site_dir, exist_ok=True)

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

            # Get blocks from MongoDB
            blocks = list(
                mongo_db.blocks.find(
                    {"page_id": page_id},
                    {"_id": 0, "page_id": 0},
                ).sort("order", 1)
            )

            # Generate HTML
            if template:
                html = template.render(
                    title=title,
                    site_name=site_name,
                    blocks=blocks,
                    published_at=datetime.utcnow().isoformat(),
                )
            else:
                # Fallback: JSON dump for debugging
                html = _generate_fallback_html(title, site_name, blocks)

            # Write file
            if slug == "/":
                filepath = os.path.join(site_dir, "index.html")
            else:
                page_dir = os.path.join(site_dir, slug.strip("/"))
                os.makedirs(page_dir, exist_ok=True)
                filepath = os.path.join(page_dir, "index.html")

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html)

        mongo_client.close()

        return {
            "site_id": site_id,
            "pages_published": len(pages_data),
            "publish_dir": site_dir,
        }

    except Exception as exc:
        self.retry(exc=exc, countdown=30)


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
