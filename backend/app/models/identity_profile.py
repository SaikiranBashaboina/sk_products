"""Identity Profile model for users with IDENTITY role."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class IdentityProfile(Base):
    __tablename__ = "identity_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    identity_uuid = Column(String(36), unique=True, nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    created_by = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="identity_profile")

    def __repr__(self):
        return f"<IdentityProfile {self.identity_uuid}>"