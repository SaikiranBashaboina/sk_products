"""Authentication service implementing business logic."""

from datetime import datetime, timedelta
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings
from app.models.user import User
import uuid


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def authenticate(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate user and return token with user data."""
        user = self.user_repo.get_by_email(email)
        if not user:
            return None

        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.utcnow():
            return None

        if not verify_password(password, user.password_hash):
            # Increment failed login attempts
            user.failed_login_attempts += 1

            # Lock account after max attempts
            if user.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
                user.locked_until = datetime.utcnow() + timedelta(minutes=settings.ACCOUNT_LOCKOUT_MINUTES)
                user.failed_login_attempts = 0  # Reset counter

            self.db.commit()
            return None

        # Reset failed attempts on successful login
        if user.failed_login_attempts > 0:
            user.failed_login_attempts = 0
            user.locked_until = None
            self.db.commit()

        if not user.active:
            return None

        roles = self.user_repo.get_user_roles(user.id)
        identity_profile = self.user_repo.get_identity_profile(user.id)

        token_data = {
            "sub": user.id,
            "email": user.email,
            "roles": roles
        }
        access_token = create_access_token(data=token_data)

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
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
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat()
            }
        }

    def get_current_user(self, user_id: str) -> Optional[Dict]:
        """Get current user data from user_id."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return None

        roles = self.user_repo.get_user_roles(user.id)
        identity_profile = self.user_repo.get_identity_profile(user.id)

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
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat()
        }

    def create_user(self, user_data: dict, created_by: Optional[str] = None) -> Dict:
        """Create a new user with password hashing."""
        # Check if email exists
        existing = self.user_repo.get_by_email(user_data["email"])
        if existing:
            raise ValueError("Email already registered")

        # Hash password
        password_hash = get_password_hash(user_data.pop("password"))

        user_dict = {
            "id": str(uuid.uuid4()),
            "uuid": str(uuid.uuid4()),
            "name": user_data["name"],
            "email": user_data["email"],
            "phone": user_data.get("phone"),
            "address": user_data.get("address"),
            "profile_image": user_data.get("profile_image"),
            "password_hash": password_hash,
            "active": True
        }

        user = self.user_repo.create(user_dict)

        # Users are created as normal users. Roles are assigned separately via Role Management.
        roles = self.user_repo.get_user_roles(user.id)
        identity_profile = self.user_repo.get_identity_profile(user.id)

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
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat()
        }