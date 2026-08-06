"""User model."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer
from sqlalchemy.dialects.sqlite import TEXT as SQLITE_TEXT
from sqlalchemy.orm import relationship
from app.database.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    uuid = Column(String(36), unique=True, default=generate_uuid, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    profile_image = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    user_orders = relationship("UserOrder", back_populates="user", cascade="all, delete-orphan")
    identity_profile = relationship("IdentityProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"