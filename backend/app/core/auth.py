"""
JWT authentication - validates tokens via the parent project API (app.akm-advisor.com).
Uses in-memory cache to avoid hitting external API on every request.
"""

import time
from typing import Dict, Tuple

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core import settings


security = HTTPBearer()

# Cache: token -> (CurrentUser, expiry_timestamp)
# TTL = 5 minutes — balance between security and performance
_TOKEN_CACHE: Dict[str, Tuple["CurrentUser", float]] = {}
_CACHE_TTL = 300  # seconds

EXTERNAL_AUTH_ME = f"{settings.EXTERNAL_AUTH_URL}/api/v1/auth/me"


class CurrentUser:
    """Represents the authenticated user from the parent project."""

    def __init__(
        self,
        user_id: str,
        email: str = "",
        name: str = "",
        tenant_id: str = "",
        role: str = "",
    ):
        self.user_id = user_id
        self.email = email
        self.name = name
        self.tenant_id = tenant_id
        self.role = role


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    """
    Validate JWT token by calling the parent project's /api/v1/auth/me.
    Results are cached for 5 minutes to reduce latency.
    """
    token = credentials.credentials

    # Check cache first
    cached = _TOKEN_CACHE.get(token)
    if cached:
        user, expires_at = cached
        if time.time() < expires_at:
            return user
        else:
            del _TOKEN_CACHE[token]

    # Validate against external auth service
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                EXTERNAL_AUTH_ME,
                headers={"Authorization": f"Bearer {token}"},
            )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cannot reach auth service",
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

    data = response.json()
    user = CurrentUser(
        user_id=str(data.get("id", data.get("sub", ""))),
        email=data.get("email", ""),
        name=data.get("full_name", data.get("name", "")),
        tenant_id=data.get("tenant_id", ""),
        role=data.get("role", ""),
    )

    if not user.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user id",
        )

    # Store in cache
    _TOKEN_CACHE[token] = (user, time.time() + _CACHE_TTL)

    # Cleanup old entries (keep cache bounded)
    if len(_TOKEN_CACHE) > 1000:
        now = time.time()
        expired = [k for k, (_, exp) in _TOKEN_CACHE.items() if exp < now]
        for k in expired:
            del _TOKEN_CACHE[k]

    return user

