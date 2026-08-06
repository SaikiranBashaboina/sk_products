"""Order model."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Numeric, Integer, Text, DateTime
from sqlalchemy.orm import relationship
from app.database.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class Order(Base):
    __tablename__ = "orders"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    uuid = Column(String(36), unique=True, default=generate_uuid, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    quantity = Column(Integer, nullable=False, default=1)
    price = Column(Numeric(10, 2), nullable=False, default=0.0)
    image = Column(String(255), nullable=True)
    stock_status = Column(String(20), default="IN_STOCK", nullable=False)
    created_by_admin = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user_orders = relationship("UserOrder", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order {self.title}>"