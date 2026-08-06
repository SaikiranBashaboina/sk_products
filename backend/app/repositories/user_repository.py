"""User repository implementing Repository pattern."""

from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.models.identity_profile import IdentityProfile
import uuid


class UserRepository:
    """Repository for User database operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_uuid(self, uuid_str: str) -> Optional[User]:
        return self.db.query(User).filter(User.uuid == uuid_str).first()

    def get_all(self, page: int = 1, page_size: int = 10, search: Optional[str] = None) -> Tuple[List[User], int]:
        query = self.db.query(User)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    User.name.ilike(search_term),
                    User.email.ilike(search_term),
                    User.phone.ilike(search_term)
                )
            )
        total = query.count()
        users = query.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return users, total

    def create(self, user_data: dict) -> User:
        user = User(**user_data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user_id: str, user_data: dict) -> Optional[User]:
        user = self.get_by_id(user_id)
        if not user:
            return None
        for key, value in user_data.items():
            if value is not None:
                setattr(user, key, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user_id: str) -> bool:
        user = self.get_by_id(user_id)
        if not user:
            return False
        self.db.delete(user)
        self.db.commit()
        return True

    def get_user_roles(self, user_id: str) -> List[str]:
        user_roles = self.db.query(UserRole).filter(UserRole.user_id == user_id).all()
        role_ids = [ur.role_id for ur in user_roles]
        roles = self.db.query(Role).filter(Role.id.in_(role_ids)).all() if role_ids else []
        return [role.name for role in roles]

    def set_user_roles(self, user_id: str, role_names: List[str]) -> List[str]:
        # Remove existing roles
        self.db.query(UserRole).filter(UserRole.user_id == user_id).delete()
        # Add new roles
        for role_name in role_names:
            role = self.db.query(Role).filter(Role.name == role_name).first()
            if role:
                user_role = UserRole(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    role_id=role.id
                )
                self.db.add(user_role)
        self.db.commit()
        return self.get_user_roles(user_id)

    def get_identity_profile(self, user_id: str) -> Optional[IdentityProfile]:
        return self.db.query(IdentityProfile).filter(IdentityProfile.user_id == user_id).first()

    def create_identity_profile(self, user_id: str, created_by: str) -> IdentityProfile:
        identity_uuid = f"ID-{uuid.uuid4().hex[:8].upper()}"
        profile = IdentityProfile(
            id=str(uuid.uuid4()),
            identity_uuid=identity_uuid,
            user_id=user_id,
            created_by=created_by
        )
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile