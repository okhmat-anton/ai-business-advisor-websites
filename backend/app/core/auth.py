"""
JWT authentication - validates tokens from the parent project (app.akm-advisor.com).
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from app.core import settings


security = HTTPBearer()


class CurrentUser:
    """Represents the authenticated user from JWT."""

    def __init__(self, user_id: str, email: str = "", name: str = ""):
        self.user_id = user_id
        self.email = email
        self.name = name


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    """
    Decode and validate JWT token from the parent project.
    Returns CurrentUser with user_id extracted from the token.
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id: str = payload.get("sub", "")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject",
            )
        return CurrentUser(
            user_id=user_id,
            email=payload.get("email", ""),
            name=payload.get("name", ""),
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
