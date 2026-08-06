"""User service implementing business logic."""

from typing import Optional, Dict, List, Tuple
from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.core.security import get_password_hash, verify_password
from app.models.user import User
import uuid


class UserService:
    """Service for user management operations."""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def get_users(self, page: int, page_size: int, search: Optional[str] = None) -> Dict:
        """Get paginated list of users."""
        users, total = self.user_repo.get_all(page, page_size, search)

        user_list = []
        for user in users:
            roles = self.user_repo.get_user_roles(user.id)
            identity_profile = self.user_repo.get_identity_profile(user.id)
            user_list.append({
                "id": user.id,
                "uuid": user.uuid,
                "name": user.name,
                "email": user.email,
                "phone": user.phone,
                "address": user.address,
                "profile_image": user.profile_image,
                "active": user.active,
                "roles": roles,
                "identity_uuid": identity_profile.identity_uuid if identity_profile else None,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat()
            })

        return {
            "users": user_list,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get a single user by ID."""
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
            "active": user.active,
            "roles": roles,
            "identity_uuid": identity_profile.identity_uuid if identity_profile else None,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat()
        }

    def update_user(self, user_id: str, user_data: dict) -> Optional[Dict]:
        """Update a user's profile."""
        # Check email uniqueness if changing email
        if "email" in user_data and user_data["email"]:
            existing = self.user_repo.get_by_email(user_data["email"])
            if existing and existing.id != user_id:
                raise ValueError("Email already in use")

        user = self.user_repo.update(user_id, user_data)
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
            "active": user.active,
            "roles": roles,
            "identity_uuid": identity_profile.identity_uuid if identity_profile else None,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat()
        }

    def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        return self.user_repo.delete(user_id)

    def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """Change user's password."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False
        if not verify_password(current_password, user.password_hash):
            return False

        new_hash = get_password_hash(new_password)
        self.user_repo.update(user_id, {"password_hash": new_hash})
        return True

    def reset_password(self, user_id: str, new_password: str) -> bool:
        """Reset user's password (admin/identity operation)."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False

        new_hash = get_password_hash(new_password)
        self.user_repo.update(user_id, {"password_hash": new_hash})
        return True

    def set_user_roles(self, user_id: str, role_names: List[str]) -> List[str]:
        """Set user roles."""
        roles = self.user_repo.set_user_roles(user_id, role_names)

        # Handle identity profile
        if "IDENTITY" in role_names:
            existing_profile = self.user_repo.get_identity_profile(user_id)
            if not existing_profile:
                self.user_repo.create_identity_profile(user_id, user_id)
        else:
            # Remove identity profile if IDENTITY role removed
            profile = self.user_repo.get_identity_profile(user_id)
            if profile:
                self.db.delete(profile)
                self.db.commit()

        return roles