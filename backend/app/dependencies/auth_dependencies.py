"""Authentication and authorization dependencies."""

from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.core.security import decode_access_token
from app.repositories.user_repository import UserRepository

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    """Dependency to get current authenticated user."""
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    roles = user_repo.get_user_roles(user.id)
    identity_profile = user_repo.get_identity_profile(user.id)

    return {
        "id": user.id,
        "uuid": user.uuid,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "address": user.address,
        "profile_image": user.profile_image,
        "roles": roles,
        "identity_uuid": identity_profile.identity_uuid if identity_profile else None,
        "active": user.active,
    }


def has_roles(required_roles: List[str]):
    """Dependency factory to check if user has required roles."""
    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_roles = current_user.get("roles", [])
        has_role = any(role in user_roles for role in required_roles)
        if not has_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user
    return role_checker


# Pre-defined role checkers
require_admin = has_roles(["ADMIN"])
require_identity = has_roles(["IDENTITY"])
require_admin_or_identity = has_roles(["ADMIN", "IDENTITY"])