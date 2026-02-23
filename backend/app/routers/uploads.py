"""
File upload router - handles image and ZIP file uploads.
"""

import os
import uuid
from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

from app.core import settings
from app.core.auth import get_current_user, CurrentUser

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("")
async def upload_file(
    file: UploadFile = File(...),
    user: CurrentUser = Depends(get_current_user),
):
    """Upload a file (image, ZIP, etc.)."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    # Check file size
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="File too large")

    # Create upload directory for user
    user_dir = os.path.join(settings.UPLOAD_DIR, user.user_id)
    os.makedirs(user_dir, exist_ok=True)

    # Generate unique filename
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(user_dir, filename)

    # Save file
    with open(filepath, "wb") as f:
        f.write(content)

    url = f"/api/v1/uploads/{user.user_id}/{filename}"
    return {"url": url, "filename": filename, "size": len(content)}


@router.get("/{user_id}/{filename}")
async def get_uploaded_file(user_id: str, filename: str):
    """Serve an uploaded file."""
    filepath = os.path.join(settings.UPLOAD_DIR, user_id, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(filepath)
