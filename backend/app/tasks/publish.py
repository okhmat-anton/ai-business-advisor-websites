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

        # Detect and strip common directory prefix from slugs
        # (artifact from ZIP folder structure, e.g. 'akm-advisor-landing/')
        non_home_slugs = [
            p.get("slug", "").strip("/")
            for p in pages_data
            if not p.get("is_home_page")
            and p.get("slug", "").strip("/") not in ("", "index")
        ]
        slug_prefix = ""
        if non_home_slugs:
            first = non_home_slugs[0]
            slash = first.find("/")
            if slash > 0:
                candidate = first[: slash + 1]
                if all(s.startswith(candidate) for s in non_home_slugs):
                    slug_prefix = candidate
                    logger.info(f"PUBLISH: stripping common slug prefix '{slug_prefix}'")

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
            raw_slug = page_info.get("slug", "/")
            # Strip detected common prefix (e.g. 'akm-advisor-landing/')
            clean = raw_slug.strip("/")
            if slug_prefix and clean.startswith(slug_prefix):
                clean = clean[len(slug_prefix):]
            slug = clean or "/"
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
    html = re.sub(r"'\s*\+\s*t_getRootZone\(\)\s*\+\s*'", 'com', html)
    # Pattern: "+t_getRootZone()+"  (double-quote variant)
    html = re.sub(r'"\s*\+\s*t_getRootZone\(\)\s*\+\s*"', 'com', html)
    # Fallback: bare t_getRootZone() call
    html = html.replace('t_getRootZone()', "'com'")
    return html


def _generate_fallback_html(title: str, site_name: str, blocks: list) -> str:
    """
    Generate styled static HTML from block data.
    Handles all block types: cover, about, text, heading, image, gallery,
    button, form, menu, footer, video, divider, columns, zeroblock.
    """
    import html as html_lib

    def esc(v) -> str:
        return html_lib.escape(str(v)) if v else ""

    blocks_html = ""
    for block in blocks:
        content = block.get("content", {})
        settings = block.get("settings", {})
        block_type = block.get("type", "")
        bg = esc(settings.get("backgroundColor", "#ffffff"))
        pt = esc(settings.get("paddingTop", "60px"))
        pb = esc(settings.get("paddingBottom", "60px"))
        section_style = f"background-color:{bg};padding:{pt} 0 {pb};"

        inner = ""

        # ── Cover blocks ───────────────────────────────────────────────────
        if block_type.startswith("CoverBlock"):
            bg_img = content.get("backgroundImage", "")
            overlay = content.get("overlayOpacity", 0.5)
            t = esc(content.get("title", ""))
            sub = esc(content.get("subtitle", ""))
            btn_text = esc(content.get("buttonText", ""))
            btn_url = esc(content.get("buttonUrl", "#"))
            cover_style = f"position:relative;min-height:540px;display:flex;align-items:center;justify-content:center;text-align:center;"
            if bg_img:
                cover_style += f"background-image:url('{esc(bg_img)}');background-size:cover;background-position:center;"
            overlay_div = f'<div style="position:absolute;inset:0;background:rgba(0,0,0,{overlay});"></div>' if bg_img else ""
            btn_html = f'<a href="{btn_url}" style="display:inline-block;margin-top:24px;padding:14px 32px;background:#1976d2;color:#fff;border-radius:6px;text-decoration:none;font-size:16px;font-weight:600;">{btn_text}</a>' if btn_text else ""
            inner = f'''
<div style="{cover_style}background-color:{bg};">
  {overlay_div}
  <div style="position:relative;z-index:1;padding:40px;max-width:800px;">
    <h1 style="font-size:clamp(2rem,5vw,3.5rem);font-weight:800;color:#fff;margin-bottom:16px;line-height:1.2;">{t}</h1>
    {"<p style='font-size:1.2rem;color:rgba(255,255,255,0.85);max-width:600px;margin:0 auto;line-height:1.6;'>" + sub + "</p>" if sub else ""}
    {btn_html}
  </div>
</div>'''
            blocks_html += inner
            continue

        # ── Menu / Navigation blocks ───────────────────────────────────────
        elif block_type.startswith("MenuBlock"):
            logo = esc(content.get("logo", ""))
            links = content.get("links", [])
            cta = content.get("ctaButton", {})
            links_html = " ".join(
                f'<a href="{esc(lnk.get("url","#"))}" style="color:#212121;text-decoration:none;font-size:15px;font-weight:500;padding:0 12px;">{esc(lnk.get("text",""))}</a>'
                for lnk in links
            )
            cta_html = f'<a href="{esc(cta.get("url","#"))}" style="background:#1976d2;color:#fff;padding:8px 22px;border-radius:6px;text-decoration:none;font-size:14px;font-weight:600;">{esc(cta.get("text",""))}</a>' if cta and cta.get("text") else ""
            inner = f'''
<nav style="background-color:{bg};padding:0;box-shadow:0 1px 4px rgba(0,0,0,0.08);">
  <div style="max-width:1200px;margin:0 auto;padding:0 40px;height:64px;display:flex;align-items:center;justify-content:space-between;">
    <span style="font-size:20px;font-weight:800;color:#1976d2;">{logo}</span>
    <div style="display:flex;align-items:center;gap:4px;">{links_html}</div>
    {cta_html}
  </div>
</nav>'''

        # ── Footer blocks ──────────────────────────────────────────────────
        elif block_type == "FooterBlock01":
            copyright = esc(content.get("copyright", ""))
            social = content.get("socialLinks", [])
            # Map MDI icon names to Unicode symbols
            icon_map = {
                "mdi-facebook": "Facebook", "mdi-twitter": "Twitter",
                "mdi-instagram": "Instagram", "mdi-linkedin": "LinkedIn",
                "mdi-youtube": "YouTube", "mdi-telegram": "Telegram",
            }
            socials_html = " ".join(
                f'<a href="{esc(s.get("url","#"))}" style="color:rgba(255,255,255,0.7);text-decoration:none;font-size:13px;padding:0 8px;">{icon_map.get(s.get("icon",""), s.get("icon",""))}</a>'
                for s in social
            ) if social else ""
            inner = f'''
<footer style="{section_style}">
  <div style="max-width:1200px;margin:0 auto;padding:0 40px;text-align:center;">
    {"<div style='margin-bottom:16px;'>" + socials_html + "</div>" if socials_html else ""}
    <p style="font-size:14px;color:rgba(255,255,255,0.5);">{copyright}</p>
  </div>
</footer>'''

        elif block_type == "FooterBlock02":
            logo = esc(content.get("logo", ""))
            desc = esc(content.get("description", ""))
            columns = content.get("columns", [])
            copyright = esc(content.get("copyright", ""))
            cols_html = ""
            for col in columns:
                col_title = esc(col.get("title", ""))
                col_links = "".join(
                    f'<li style="margin-bottom:10px;"><a href="{esc(lnk.get("url","#"))}" style="color:rgba(255,255,255,0.5);text-decoration:none;font-size:14px;">{esc(lnk.get("text",""))}</a></li>'
                    for lnk in col.get("links", [])
                )
                cols_html += f'<div style="flex:1;min-width:140px;"><h4 style="font-size:12px;text-transform:uppercase;letter-spacing:1px;color:rgba(255,255,255,0.8);margin-bottom:16px;">{col_title}</h4><ul style="list-style:none;padding:0;margin:0;">{col_links}</ul></div>'
            inner = f'''
<footer style="{section_style}">
  <div style="max-width:1200px;margin:0 auto;padding:0 40px;">
    <div style="display:flex;flex-wrap:wrap;gap:40px;margin-bottom:40px;">
      <div style="flex:1.5;min-width:200px;">
        <h3 style="font-size:22px;color:#fff;margin-bottom:10px;">{logo}</h3>
        <p style="font-size:14px;color:rgba(255,255,255,0.6);line-height:1.6;">{desc}</p>
      </div>
      {cols_html}
    </div>
    <div style="border-top:1px solid rgba(255,255,255,0.1);padding-top:20px;">
      <p style="font-size:13px;color:rgba(255,255,255,0.4);">{copyright}</p>
    </div>
  </div>
</footer>'''

        # ── Text / Heading / About blocks ──────────────────────────────────
        elif block_type in ("TextBlock01", "TextBlock02", "AboutBlock01", "AboutBlock02",
                            "HeadingBlock01"):
            t = esc(content.get("title", ""))
            sub = esc(content.get("subtitle", content.get("text", "")))
            align = settings.get("align", "center")
            left_text = esc(content.get("leftText", ""))
            right_text = esc(content.get("rightText", ""))
            img = esc(content.get("image", ""))
            counters = content.get("counters", [])
            level = content.get("level", "h2")

            body_parts = []
            if t:
                tag = level if level in ("h1","h2","h3","h4") else "h2"
                body_parts.append(f'<{tag} style="font-size:clamp(1.6rem,3vw,2.5rem);font-weight:700;color:#212121;margin-bottom:16px;">{t}</{tag}>')
            if sub:
                body_parts.append(f'<p style="color:#555;line-height:1.7;font-size:16px;max-width:720px;margin:0 auto 20px;">{sub}</p>')
            if left_text or right_text:
                body_parts.append(f'<div style="display:flex;gap:40px;text-align:left;"><div style="flex:1"><p style="color:#555;line-height:1.7;">{left_text}</p></div><div style="flex:1"><p style="color:#555;line-height:1.7;">{right_text}</p></div></div>')
            if img:
                body_parts.append(f'<img src="{img}" style="max-width:100%;width:500px;border-radius:12px;" alt="" />')
            if counters:
                ctrs = "".join(f'<div style="flex:1;min-width:120px;"><div style="font-size:2rem;font-weight:800;color:#1976d2;">{esc(c.get("value",""))}</div><div style="color:#888;font-size:14px;margin-top:4px;">{esc(c.get("label",""))}</div></div>' for c in counters)
                body_parts.append(f'<div style="display:flex;flex-wrap:wrap;gap:20px;justify-content:center;margin-top:32px;">{ctrs}</div>')
            inner = f'<section style="{section_style}"><div style="max-width:1100px;margin:0 auto;padding:0 40px;text-align:{align};">{"".join(body_parts)}</div></section>'

        # ── Image block ────────────────────────────────────────────────────
        elif block_type == "ImageBlock01":
            img = esc(content.get("image", ""))
            alt = esc(content.get("alt", ""))
            caption = esc(content.get("caption", ""))
            inner = f'<section style="{section_style}"><div style="max-width:1100px;margin:0 auto;padding:0 40px;text-align:center;">{"<img src=\'" + img + "\' alt=\'" + alt + "\' style=\'max-width:100%;border-radius:8px;\' />" if img else ""}{"<p style=\'color:#888;font-size:13px;margin-top:10px;\'>" + caption + "</p>" if caption else ""}</div></section>'

        # ── Gallery block ──────────────────────────────────────────────────
        elif block_type == "GalleryBlock01":
            images = content.get("images", [])
            cols = int(content.get("columns", 2))
            imgs_html = "".join(f'<img src="{esc(img.get("src",""))}" alt="{esc(img.get("alt",""))}" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:8px;" />' for img in images)
            inner = f'<section style="{section_style}"><div style="max-width:1100px;margin:0 auto;padding:0 40px;"><div style="display:grid;grid-template-columns:repeat({cols},1fr);gap:16px;">{imgs_html}</div></div></section>'

        # ── Button block ───────────────────────────────────────────────────
        elif block_type == "ButtonBlock01":
            buttons = content.get("buttons", [])
            btns = ""
            for btn in buttons:
                style_ = btn.get("style", "primary")
                if style_ == "primary":
                    bstyle = "background:#1976d2;color:#fff;border:none;"
                elif style_ == "outlined":
                    bstyle = "background:transparent;color:#1976d2;border:2px solid #1976d2;"
                else:
                    bstyle = "background:#f5f5f5;color:#212121;border:none;"
                btns += f'<a href="{esc(btn.get("url","#"))}" style="{bstyle}display:inline-block;padding:14px 32px;border-radius:6px;text-decoration:none;font-size:16px;font-weight:600;margin:6px;">{esc(btn.get("text",""))}</a>'
            inner = f'<section style="{section_style}"><div style="max-width:1100px;margin:0 auto;padding:0 40px;text-align:center;">{btns}</div></section>'

        # ── Form blocks ────────────────────────────────────────────────────
        elif block_type in ("FormBlock01", "FormBlock02", "CrmFormBlock"):
            t = esc(content.get("title", ""))
            sub = esc(content.get("subtitle", ""))
            embed = content.get("embedCode", "")
            fields = content.get("fields", [])
            submit = esc(content.get("submitText", "Submit"))
            if embed:
                # CRM form - include raw embed code
                inner = f'<section style="{section_style}"><div style="max-width:640px;margin:0 auto;padding:0 40px;">{"<h2 style=\'text-align:center;font-size:1.8rem;font-weight:700;margin-bottom:8px;\'>" + t + "</h2>" if t else ""}{"<p style=\'text-align:center;color:#666;margin-bottom:24px;\'>" + sub + "</p>" if sub else ""}{embed}</div></section>'
            else:
                fields_html = ""
                for f_ in fields:
                    lbl = esc(f_.get("label", ""))
                    ph = esc(f_.get("placeholder", ""))
                    ftype = f_.get("type", "text")
                    if ftype == "textarea":
                        fields_html += f'<div style="margin-bottom:16px;"><label style="display:block;font-size:14px;font-weight:500;margin-bottom:6px;color:#374151;">{lbl}</label><textarea placeholder="{ph}" style="width:100%;padding:10px 14px;border:1px solid #d1d5db;border-radius:6px;font-size:15px;resize:vertical;min-height:120px;"></textarea></div>'
                    else:
                        fields_html += f'<div style="margin-bottom:16px;"><label style="display:block;font-size:14px;font-weight:500;margin-bottom:6px;color:#374151;">{lbl}</label><input type="{ftype}" placeholder="{ph}" style="width:100%;padding:10px 14px;border:1px solid #d1d5db;border-radius:6px;font-size:15px;" /></div>'
                form_placeholder = f'<p style="color:#999;font-size:14px;text-align:center;">Form fields preview only – not functional in static export.</p>' if not fields_html and not embed else ""
                inner = f'<section style="{section_style}"><div style="max-width:600px;margin:0 auto;padding:0 40px;">{"<h2 style=\'text-align:center;font-size:2rem;font-weight:700;margin-bottom:8px;\'>" + t + "</h2>" if t else ""}{"<p style=\'text-align:center;color:#666;margin-bottom:32px;\'>" + sub + "</p>" if sub else ""}{form_placeholder}<form>{fields_html}{"<button type=\'submit\' style=\'width:100%;padding:13px;background:#1976d2;color:#fff;border:none;border-radius:6px;font-size:16px;font-weight:600;cursor:pointer;\'>" + submit + "</button>" if fields_html else ""}</form></div></section>'

        # ── Video block ────────────────────────────────────────────────────
        elif block_type == "VideoBlock01":
            url = esc(content.get("videoUrl", ""))
            t = esc(content.get("title", ""))
            inner = f'<section style="{section_style}"><div style="max-width:900px;margin:0 auto;padding:0 40px;text-align:center;">{"<h2 style=\'font-size:1.8rem;font-weight:700;color:#fff;margin-bottom:24px;\'>" + t + "</h2>" if t else ""}{"<div style=\'position:relative;padding-bottom:56.25%;height:0;overflow:hidden;border-radius:12px;\'><iframe src=\'" + url + "\' style=\'position:absolute;top:0;left:0;width:100%;height:100%;border:none;\' allowfullscreen></iframe></div>" if url else ""}</div></section>'

        # ── Divider block ──────────────────────────────────────────────────
        elif block_type == "DividerBlock01":
            color = esc(content.get("color", "#e0e0e0"))
            inner = f'<div style="padding:{pt} 40px {pb};background-color:{bg};"><hr style="border:none;border-top:1px solid {color};max-width:1100px;margin:0 auto;" /></div>'

        # ── Columns block ──────────────────────────────────────────────────
        elif block_type == "ColumnsBlock01":
            columns = content.get("columns", [])
            cols_html = ""
            for col in columns:
                col_t = esc(col.get("title", ""))
                col_txt = esc(col.get("text", ""))
                col_icon = esc(col.get("icon", ""))
                cols_html += f'<div style="flex:1;min-width:200px;text-align:center;padding:20px;">{"<div style=\'font-size:40px;margin-bottom:12px;\'>" + col_icon + "</div>" if col_icon else ""}{"<h3 style=\'font-size:1.2rem;font-weight:600;margin-bottom:10px;\'>" + col_t + "</h3>" if col_t else ""}{"<p style=\'color:#666;line-height:1.6;\'>" + col_txt + "</p>" if col_txt else ""}</div>'
            inner = f'<section style="{section_style}"><div style="max-width:1100px;margin:0 auto;padding:0 20px;"><div style="display:flex;flex-wrap:wrap;gap:24px;">{cols_html}</div></div></section>'

        # ── ZeroBlock (HTML embed) ─────────────────────────────────────────
        elif block_type == "ZeroBlock":
            html_code = content.get("html", "")
            inner = f'<section style="{section_style}"><div style="max-width:1200px;margin:0 auto;">{html_code}</div></section>'

        # ── Generic fallback ───────────────────────────────────────────────
        else:
            t = esc(content.get("title", ""))
            sub = esc(content.get("subtitle", content.get("text", "")))
            if t or sub:
                inner = f'<section style="{section_style}"><div style="max-width:1100px;margin:0 auto;padding:0 40px;text-align:center;">{"<h2 style=\'font-size:2rem;font-weight:700;color:#212121;margin-bottom:16px;\'>" + t + "</h2>" if t else ""}{"<p style=\'color:#555;line-height:1.7;\'>" + sub + "</p>" if sub else ""}</div></section>'

        blocks_html += inner

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{esc(title)} – {esc(site_name)}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color: #212121; line-height: 1.5; }}
        img {{ display: block; }}
        a {{ text-decoration: none; }}
        @media (max-width: 768px) {{
            nav div {{ flex-wrap: wrap; gap: 8px; }}
            div[style*="display:flex"] {{ flex-direction: column; }}
        }}
    </style>
</head>
<body>
{blocks_html}
</body>
</html>"""
