"""User-Order association model."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class UserOrder(Base):
    __tablename__ = "user_orders"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    order_id = Column(String(36), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(SQLEnum("ORDERED", "PROCESSED", "DELIVERED", "CANCELLED", name="user_order_status"), default="ORDERED", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="user_orders")
    order = relationship("Order", back_populates="user_orders")

    def __repr__(self):
        return f"<UserOrder user={self.user_id} order={self.order_id} status={self.status}>"