"""Order repository implementing Repository pattern."""

from typing import Optional, List, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from app.models.order import Order
from app.models.user_order import UserOrder
from app.models.user import User
import uuid


class OrderRepository:
    """Repository for Order database operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, order_id: str) -> Optional[Order]:
        return self.db.query(Order).filter(Order.id == order_id).first()

    def get_all(self, page: int = 1, page_size: int = 10, search: Optional[str] = None) -> Tuple[List[Order], int]:
        query = self.db.query(Order)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Order.title.ilike(search_term),
                    Order.description.ilike(search_term)
                )
            )
        total = query.count()
        orders = query.order_by(Order.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return orders, total

    def create(self, order_data: dict) -> Order:
        order = Order(**order_data)
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order

    def update(self, order_id: str, order_data: dict) -> Optional[Order]:
        order = self.get_by_id(order_id)
        if not order:
            return None
        for key, value in order_data.items():
            if value is not None:
                setattr(order, key, value)
        self.db.commit()
        self.db.refresh(order)
        return order

    def delete(self, order_id: str) -> bool:
        order = self.get_by_id(order_id)
        if not order:
            return False
        self.db.delete(order)
        self.db.commit()
        return True

    def select_order(self, user_id: str, order_id: str) -> UserOrder:
        """Create a new order selection. Users can place unlimited orders."""
        user_order = UserOrder(
            id=str(uuid.uuid4()),
            user_id=user_id,
            order_id=order_id,
            status="ORDERED"
        )
        self.db.add(user_order)
        self.db.commit()
        self.db.refresh(user_order)
        return user_order

    def get_user_orders(self, user_id: str, page: int = 1, page_size: int = 10) -> Tuple[List[UserOrder], int]:
        query = self.db.query(UserOrder).filter(UserOrder.user_id == user_id)
        total = query.count()
        user_orders = query.options(joinedload(UserOrder.order)).order_by(
            UserOrder.created_at.desc()
        ).offset((page - 1) * page_size).limit(page_size).all()
        return user_orders, total

    def get_all_user_orders(self, page: int = 1, page_size: int = 10, status: Optional[str] = None) -> Tuple[List[UserOrder], int]:
        query = self.db.query(UserOrder).options(
            joinedload(UserOrder.order),
            joinedload(UserOrder.user)
        )
        if status:
            query = query.filter(UserOrder.status == status)
        total = query.count()
        user_orders = query.order_by(UserOrder.created_at.desc()).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
        return user_orders, total

    def get_user_order_by_id(self, user_order_id: str) -> Optional[UserOrder]:
        return self.db.query(UserOrder).options(
            joinedload(UserOrder.order),
            joinedload(UserOrder.user)
        ).filter(UserOrder.id == user_order_id).first()

    def update_user_order_status(self, user_order_id: str, status: str) -> Optional[UserOrder]:
        user_order = self.db.query(UserOrder).filter(UserOrder.id == user_order_id).first()
        if not user_order:
            return None
        user_order.status = status
        self.db.commit()
        self.db.refresh(user_order)
        return user_order

    def cancel_user_order(self, user_order_id: str, user_id: str) -> Optional[UserOrder]:
        user_order = self.db.query(UserOrder).filter(
            UserOrder.id == user_order_id,
            UserOrder.user_id == user_id,
            UserOrder.status == "ORDERED"
        ).first()
        if not user_order:
            return None
        user_order.status = "CANCELLED"
        self.db.commit()
        self.db.refresh(user_order)
        return user_order