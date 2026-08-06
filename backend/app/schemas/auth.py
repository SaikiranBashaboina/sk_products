"""Pydantic schemas for Authentication."""

from typing import Optional, List
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str = Field(..., max_length=100)
    password: str = Field(..., max_length=100)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict
    refresh_token: Optional[str] = None
    refresh_token_expires_in: Optional[int] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., max_length=255)


class RoleAssignment(BaseModel):
    roles: List[str] = Field(default=[])
