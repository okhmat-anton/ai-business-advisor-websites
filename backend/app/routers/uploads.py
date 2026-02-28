"""
File upload router — handles image and other file uploads.
Supports local disk storage (default) and S3-compatible object storage.
Active storage backend is determined by admin settings stored in Redis.
"""

import io
import os
import uuid
import logging
from typing import Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

from app.core import settings
from app.core.auth import get_current_user, CurrentUser
from app.routers.admin import _load_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/uploads", tags=["uploads"])


# ── S3 helpers ────────────────────────────────────────────────────────────────

async def _get_s3_config() -> Optional[dict]:
    """
    Return active S3 config from admin settings if S3 is enabled.
    Falls back to env-based settings if Redis has nothing.
    Returns None when S3 is disabled.
    """
    admin = await _load_settings()
    s3 = admin.get("s3", {})

    enabled = s3.get("enabled", settings.S3_ENABLED)
    if not enabled:
        return None

    return {
        "bucket": s3.get("bucket") or settings.S3_BUCKET,
        "region": s3.get("region") or settings.S3_REGION,
        "access_key": s3.get("accessKey") or settings.S3_ACCESS_KEY,
        "secret_key": s3.get("secretKey") or settings.S3_SECRET_KEY,
        "endpoint_url": s3.get("endpointUrl") or settings.S3_ENDPOINT_URL or None,
        "public_url": s3.get("publicUrl") or settings.S3_PUBLIC_URL or None,
        "folder": s3.get("folder") or settings.S3_FOLDER,
    }


def _build_s3_client(cfg: dict):
    """Create a boto3 S3 client from config dict."""
    kwargs = {
        "aws_access_key_id": cfg["access_key"],
        "aws_secret_access_key": cfg["secret_key"],
        "region_name": cfg["region"],
    }
    if cfg.get("endpoint_url"):
        kwargs["endpoint_url"] = cfg["endpoint_url"]
    return boto3.client("s3", **kwargs)


def _s3_public_url(cfg: dict, key: str) -> str:
    """Build the public URL for an S3 object."""
    if cfg.get("public_url"):
        base = cfg["public_url"].rstrip("/")
        return f"{base}/{key}"
    # Standard AWS URL
    bucket = cfg["bucket"]
    region = cfg["region"]
    return f"https://{bucket}.s3.{region}.amazonaws.com/{key}"


async def _upload_to_s3(cfg: dict, content: bytes, filename: str, content_type: str) -> str:
    """Upload file bytes to S3 and return the public URL."""
    folder = cfg["folder"].strip("/")
    key = f"{folder}/{filename}" if folder else filename

    client = _build_s3_client(cfg)
    try:
        client.put_object(
            Bucket=cfg["bucket"],
            Key=key,
            Body=content,
            ContentType=content_type,
            ACL="public-read",
        )
    except (BotoCoreError, ClientError) as exc:
        logger.error(f"S3 upload failed: {exc}")
        raise HTTPException(status_code=502, detail=f"S3 upload error: {exc}")

    return _s3_public_url(cfg, key)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("")
async def upload_file(
    file: UploadFile = File(...),
    user: CurrentUser = Depends(get_current_user),
):
    """
    Upload a file.
    If S3 is configured in admin settings the file is stored in S3 and a
    public S3 URL is returned.  Otherwise the file is saved to local disk and
    served via /api/v1/uploads/{user_id}/{filename}.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="File too large")

    ext = os.path.splitext(file.filename)[1].lower()
    unique_name = f"{uuid.uuid4().hex}{ext}"
    content_type = file.content_type or "application/octet-stream"

    # Try S3 first
    s3_cfg = await _get_s3_config()
    if s3_cfg:
        url = await _upload_to_s3(s3_cfg, content, unique_name, content_type)
        return {"url": url, "filename": unique_name, "size": len(content), "storage": "s3"}

    # Fallback: local disk
    user_dir = os.path.join(settings.UPLOAD_DIR, user.user_id)
    os.makedirs(user_dir, exist_ok=True)
    filepath = os.path.join(user_dir, unique_name)
    with open(filepath, "wb") as f:
        f.write(content)

    url = f"/api/v1/uploads/{user.user_id}/{unique_name}"
    return {"url": url, "filename": unique_name, "size": len(content), "storage": "local"}


@router.get("/{user_id}/{filename}")
async def get_uploaded_file(user_id: str, filename: str):
    """Serve a locally-stored uploaded file."""
    filepath = os.path.join(settings.UPLOAD_DIR, user_id, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(filepath)
