"""
File upload router — handles image and other file uploads.
Files are stored on local disk and served via /api/v1/uploads/{user_id}/{filename}.
For cloud storage use the external API at https://app.akm-advisor.com/api/v1/files/upload.
"""

import os
import uuid
import logging

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

from app.core import settings
from app.core.auth import get_current_user, CurrentUser

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/uploads", tags=["uploads"])


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("")
async def upload_file(
    file: UploadFile = File(...),
    user: CurrentUser = Depends(get_current_user),
):
    """
    Upload a file to local disk storage.
    Returns a URL path that can be used to retrieve the file.
    For S3/cloud storage, the frontend should call the external API directly.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="File too large")

    ext = os.path.splitext(file.filename)[1].lower()
    unique_name = f"{uuid.uuid4().hex}{ext}"

    # Save to local disk
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
