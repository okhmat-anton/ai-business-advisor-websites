"""
Admin settings router — manage global application settings (S3, etc.).
Settings are stored in Redis under key 'admin:settings' as JSON.
"""

import json
import logging
from typing import Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.auth import get_current_user, CurrentUser
from app.core.redis import get_redis

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])

REDIS_KEY = "admin:settings"


# ── Schemas ──────────────────────────────────────────────────────────────────

class S3Settings(BaseModel):
    enabled: bool = False
    bucket: str = ""
    region: str = "us-east-1"
    accessKey: str = ""
    secretKey: str = ""
    endpointUrl: str = ""   # leave empty for real AWS S3
    publicUrl: str = ""     # base public URL; auto-built if empty
    folder: str = "uploads"


class AdminSettings(BaseModel):
    s3: S3Settings = S3Settings()


class AdminSettingsUpdate(BaseModel):
    s3: Optional[S3Settings] = None


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _load_settings() -> dict:
    """Load admin settings from Redis, return empty dict if not set."""
    redis = await get_redis()
    raw = await redis.get(REDIS_KEY)
    if raw:
        try:
            return json.loads(raw)
        except Exception:
            return {}
    return {}


async def _save_settings(data: dict) -> None:
    """Persist admin settings to Redis."""
    redis = await get_redis()
    await redis.set(REDIS_KEY, json.dumps(data))


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/settings", response_model=AdminSettings)
async def get_admin_settings(
    user: CurrentUser = Depends(get_current_user),
):
    """Return current admin settings."""
    data = await _load_settings()
    return AdminSettings(**data) if data else AdminSettings()


@router.patch("/settings", response_model=AdminSettings)
async def update_admin_settings(
    payload: AdminSettingsUpdate,
    user: CurrentUser = Depends(get_current_user),
):
    """Partial-update admin settings (only provided fields are updated)."""
    data = await _load_settings()

    update = payload.model_dump(exclude_unset=True)

    # Deep-merge s3 block
    if "s3" in update and update["s3"] is not None:
        existing_s3 = data.get("s3", {})
        existing_s3.update(update["s3"])
        data["s3"] = existing_s3

    await _save_settings(data)
    logger.info(f"Admin settings updated by user {user.user_id}")
    return AdminSettings(**data)


@router.post("/test-s3")
async def test_s3_connection(
    user: CurrentUser = Depends(get_current_user),
):
    """Test the current S3 settings by listing bucket contents (head_bucket)."""
    data = await _load_settings()
    s3_cfg = data.get("s3", {})

    if not s3_cfg.get("enabled"):
        raise HTTPException(status_code=400, detail="S3 is not enabled")

    bucket = s3_cfg.get("bucket", "")
    if not bucket:
        raise HTTPException(status_code=400, detail="Bucket name is required")

    kwargs = {
        "aws_access_key_id": s3_cfg.get("accessKey", ""),
        "aws_secret_access_key": s3_cfg.get("secretKey", ""),
        "region_name": s3_cfg.get("region", "us-east-1"),
    }
    endpoint = s3_cfg.get("endpointUrl", "").strip()
    if endpoint:
        kwargs["endpoint_url"] = endpoint

    try:
        client = boto3.client("s3", **kwargs)
        client.head_bucket(Bucket=bucket)
        return {"ok": True, "message": f"Connected to bucket '{bucket}' successfully"}
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code", "")
        msg = exc.response.get("Error", {}).get("Message", str(exc))
        raise HTTPException(status_code=400, detail=f"S3 error {code}: {msg}") from exc
    except BotoCoreError as exc:
        raise HTTPException(status_code=400, detail=f"Connection error: {exc}") from exc
