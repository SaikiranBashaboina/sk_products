"""Profile management API routes."""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from app.database.database import get_db
from app.schemas.user import UserUpdate, PasswordChange
from app.services.user_service import UserService
from app.dependencies.auth_dependencies import get_current_user
from app.utils.file_upload import save_upload_file

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("")
def get_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile."""
    return current_user


@router.put("")
def update_profile(
    request: UserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update current user profile."""
    user_service = UserService(db)
    try:
        user = user_service.update_user(current_user["id"], request.model_dump(exclude_none=True))
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/change-password")
def change_password(
    request: PasswordChange,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Change current user password."""
    user_service = UserService(db)
    success = user_service.change_password(
        current_user["id"],
        request.current_password,
        request.new_password
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    return {"message": "Password changed successfully"}


@router.post("/upload-image")
async def upload_profile_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Upload profile image."""
    filename = await save_upload_file(file)
    user_service = UserService(db)
    user = user_service.update_user(current_user["id"], {"profile_image": filename})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"profile_image": filename}