"""
Auth router - proxy to parent project (app.akm-advisor.com).
Validates JWT token and returns current user info.
"""

import httpx
from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import JSONResponse

from app.core import settings

router = APIRouter(prefix="/auth", tags=["auth"])

EXTERNAL_AUTH_ME = f"{settings.EXTERNAL_AUTH_URL}/api/v1/auth/me"


@router.get("/me")
async def get_me(request: Request):
    """
    Validate JWT token against parent project and return user info.
    Reads Bearer token from Authorization header.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization token",
        )

    token = auth_header.removeprefix("Bearer ")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                EXTERNAL_AUTH_ME,
                headers={"Authorization": f"Bearer {token}"},
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Cannot reach auth service: {e}",
        )

    if response.status_code == 401:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Auth service returned {response.status_code}",
        )

    return response.json()
