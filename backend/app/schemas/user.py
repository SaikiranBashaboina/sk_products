"""Pydantic schemas for User."""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator
from app.utils.validators import validate_email, validate_password


class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    profile_image: Optional[str] = None

    @validator("email")
    def validate_email_field(cls, v):
        return validate_email(v)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)

    @validator("password")
    def validate_password_field(cls, v):
        return validate_password(v)


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    profile_image: Optional[str] = None

    @validator("email")
    def validate_email_field(cls, v):
        if v is not None:
            return validate_email(v)
        return v


class UserResponse(UserBase):
    id: str
    uuid: str
    active: bool
    created_at: datetime
    updated_at: datetime
    roles: List[str] = []
    identity_uuid: Optional[str] = None

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    page_size: int


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=100)

    @validator("new_password")
    def validate_password_field(cls, v):
        return validate_password(v)


class PasswordReset(BaseModel):
    new_password: str = Field(..., min_length=6, max_length=100)

    @validator("new_password")
    def validate_password_field(cls, v):
        return validate_password(v)
