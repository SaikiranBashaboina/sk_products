"""User management API routes."""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse, PasswordChange, PasswordReset
from app.schemas.auth import RoleAssignment
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.dependencies.auth_dependencies import get_current_user, require_admin, require_admin_or_identity
from app.utils.file_upload import save_upload_file

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("")
def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin_or_identity)
):
    """Get all users (Admin/Identity only)."""
    user_service = UserService(db)
    return user_service.get_users(page, page_size, search)


@router.get("/{user_id}")
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin_or_identity)
):
    """Get user by ID (Admin/Identity only)."""
    user_service = UserService(db)
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("", status_code=status.HTTP_201_CREATED)
def create_user(
    request: UserCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin_or_identity)
):
    """Create a new user (Admin/Identity only)."""
    auth_service = AuthService(db)
    try:
        user = auth_service.create_user(request.model_dump(), created_by=current_user["id"])
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{user_id}")
def update_user(
    user_id: str,
    request: UserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin_or_identity)
):
    """Update user (Admin/Identity only)."""
    user_service = UserService(db)
    try:
        user = user_service.update_user(user_id, request.model_dump(exclude_none=True))
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{user_id}")
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Delete user (Admin only)."""
    user_service = UserService(db)
    success = user_service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"message": "User deleted successfully"}


@router.put("/{user_id}/roles")
def update_user_roles(
    user_id: str,
    request: RoleAssignment,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update user roles (Admin can assign any role, Identity can only assign IDENTITY role)."""
    user_service = UserService(db)
    
    # Check permissions: only ADMIN and IDENTITY can manage roles
    user_roles = current_user.get("roles", [])
    if "ADMIN" not in user_roles and "IDENTITY" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to manage roles"
        )
    
    # Identity users can only assign IDENTITY role, not ADMIN
    if "IDENTITY" in user_roles and "ADMIN" not in user_roles:
        # Identity user - only allow IDENTITY role
        if "ADMIN" in request.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Identity users cannot assign ADMIN role"
            )
        # Only allow IDENTITY role (and no other roles)
        if not all(role == "IDENTITY" for role in request.roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Identity users can only assign IDENTITY role"
            )
    
    roles = user_service.set_user_roles(user_id, request.roles)
    return {"roles": roles}


@router.post("/{user_id}/reset-password")
def reset_user_password(
    user_id: str,
    request: PasswordReset,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin_or_identity)
):
    """Reset user password (Admin/Identity only)."""
    user_service = UserService(db)
    success = user_service.reset_password(user_id, request.new_password)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"message": "Password reset successfully"}