"""Authentication API routes."""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.auth import LoginRequest, RefreshTokenRequest
from app.schemas.user import UserCreate
from app.services.auth_service import AuthService
from app.dependencies.auth_dependencies import get_current_user
from app.core.security import create_access_token, create_refresh_token, hash_refresh_token, decode_access_token
from app.core.config import settings
from app.models.token import RefreshToken
from app.models.user import User
import uuid

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token with refresh token."""
    auth_service = AuthService(db)
    result = auth_service.authenticate(request.email, request.password)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Generate refresh token
    user_id = result["user"]["id"]
    refresh_token_raw = create_refresh_token({"sub": user_id})
    refresh_token_hash = hash_refresh_token(refresh_token_raw)

    # Store refresh token in database
    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token_obj = RefreshToken(
        id=str(uuid.uuid4()),
        user_id=user_id,
        token_hash=refresh_token_hash,
        expires_at=expires_at,
        revoked=False,
    )
    db.add(refresh_token_obj)
    db.commit()

    # Return response with refresh token
    result["refresh_token"] = refresh_token_raw
    result["refresh_token_expires_in"] = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60  # in seconds

    return result


@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user."""
    return current_user


@router.post("/refresh")
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token using refresh token."""
    refresh_token_hash = hash_refresh_token(request.refresh_token)

    # Find valid refresh token
    token_obj = db.query(RefreshToken).filter(
        RefreshToken.token_hash == refresh_token_hash,
        RefreshToken.revoked == False,
        RefreshToken.expires_at > datetime.utcnow(),
    ).first()

    if not token_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # Get user
    user = db.query(User).filter(User.id == token_obj.user_id).first()
    if not user or not user.active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or deactivated",
        )

    # Generate new access token
    from app.repositories.user_repository import UserRepository
    user_repo = UserRepository(db)
    roles = user_repo.get_user_roles(user.id)
    identity_profile = user_repo.get_identity_profile(user.id)

    token_data = {
        "sub": user.id,
        "email": user.email,
        "roles": roles
    }
    access_token = create_access_token(data=token_data)

    # Optionally rotate refresh token (create new one, revoke old)
    token_obj.revoked = True
    token_obj.revoked_at = datetime.utcnow()

    new_refresh_token_raw = create_refresh_token({"sub": user.id})
    new_refresh_token_hash = hash_refresh_token(new_refresh_token_raw)
    new_expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    new_token_obj = RefreshToken(
        id=str(uuid.uuid4()),
        user_id=user.id,
        token_hash=new_refresh_token_hash,
        expires_at=new_expires_at,
        revoked=False,
    )
    db.add(new_token_obj)
    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": new_refresh_token_raw,
        "refresh_token_expires_in": settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    }


@router.post("/logout")
def logout(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Revoke refresh token (logout)."""
    refresh_token_hash = hash_refresh_token(request.refresh_token)

    token_obj = db.query(RefreshToken).filter(
        RefreshToken.token_hash == refresh_token_hash,
        RefreshToken.revoked == False,
    ).first()

    if token_obj:
        token_obj.revoked = True
        token_obj.revoked_at = datetime.utcnow()
        db.commit()

    return {"message": "Logged out successfully"}
