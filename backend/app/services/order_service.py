
"""Order service implementing business logic."""

from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from app.repositories.order_repository import OrderRepository
from app.repositories.user_repository import UserRepository
import uuid


class OrderService:
    """Service for order management operations."""

    def __init__(self, db: Session):
        self.db = db
        self.order_repo = OrderRepository(db)
        self.user_repo = UserRepository(db)

    def get_orders(self, page: int, page_size: int, search: Optional[str] = None) -> Dict:
        """Get paginated list of all orders."""
        orders, total = self.order_repo.get_all(page, page_size, search)

        order_list = []
        for order in orders:
            order_list.append({
                "id": order.id,
                "uuid": order.uuid,
                "title": order.title,
                "description": order.description,
                "quantity": order.quantity,
                "price": order.price,
                "image": order.image,
                "stock_status": order.stock_status,
                "created_by_admin": order.created_by_admin,
                "created_at": order.created_at.isoformat(),
                "updated_at": order.updated_at.isoformat()
            })

        return {
            "orders": order_list,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    def get_order(self, order_id: str) -> Optional[Dict]:
        """Get a single order by ID."""
        order = self.order_repo.get_by_id(order_id)
        if not order:
            return None

        return {
            "id": order.id,
            "uuid": order.uuid,
            "title": order.title,
            "description": order.description,
            "quantity": order.quantity,
            "price": order.price,
            "image": order.image,
            "stock_status": order.stock_status,
            "created_by_admin": order.created_by_admin,
            "created_at": order.created_at.isoformat(),
            "updated_at": order.updated_at.isoformat()
        }

    def create_order(self, order_data: dict, admin_id: str) -> Dict:
        """Create a new order."""
        order_dict = {
            "id": str(uuid.uuid4()),
            "uuid": str(uuid.uuid4()),
            "title": order_data["title"],
            "description": order_data.get("description"),
            "quantity": order_data["quantity"],
            "price": order_data["price"],
            "image": order_data.get("image"),
            "created_by_admin": admin_id
        }

        order = self.order_repo.create(order_dict)

        return {
            "id": order.id,
            "uuid": order.uuid,
            "title": order.title,
            "description": order.description,
            "quantity": order.quantity,
            "price": order.price,
            "image": order.image,
            "stock_status": order.stock_status,
            "created_by_admin": order.created_by_admin,
            "created_at": order.created_at.isoformat(),
            "updated_at": order.updated_at.isoformat()
        }

    def update_order(self, order_id: str, order_data: dict) -> Optional[Dict]:
        """Update an existing order."""
        order = self.order_repo.update(order_id, order_data)
        if not order:
            return None

        return {
            "id": order.id,
            "uuid": order.uuid,
            "title": order.title,
            "description": order.description,
            "quantity": order.quantity,
            "price": order.price,
            "image": order.image,
            "stock_status": order.stock_status,
            "created_by_admin": order.created_by_admin,
            "created_at": order.created_at.isoformat(),
            "updated_at": order.updated_at.isoformat()
        }

    def delete_order(self, order_id: str) -> bool:
        """Delete an order."""
        return self.order_repo.delete(order_id)

    def select_order(self, user_id: str, order_id: str) -> Dict:
        """User selects/orders an item. Users can place unlimited orders."""
        # Check if order is in stock
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found")
        if order.stock_status == "OUT_OF_STOCK":
            raise ValueError("This product is out of stock")

        user_order = self.order_repo.select_order(user_id, order_id)

        return {
            "id": user_order.id,
            "user_id": user_order.user_id,
            "order_id": user_order.order_id,
            "status": user_order.status,
            "created_at": user_order.created_at.isoformat(),
            "updated_at": user_order.updated_at.isoformat()
        }

    def get_my_orders(self, user_id: str, page: int, page_size: int) -> Dict:
        """Get current user's orders."""
        user_orders, total = self.order_repo.get_user_orders(user_id, page, page_size)

        items = []
        for uo in user_orders:
            order = uo.order
            items.append({
                "id": uo.id,
                "user_id": uo.user_id,
                "order_id": uo.order_id,
                "status": uo.status,
                "order": {
                    "id": order.id,
                    "uuid": order.uuid,
                    "title": order.title,
                    "description": order.description,
                    "quantity": order.quantity,
                    "price": order.price,
                    "image": order.image,
                    "stock_status": order.stock_status,
                    "created_at": order.created_at.isoformat(),
                    "updated_at": order.updated_at.isoformat()
                } if order else None,
                "created_at": uo.created_at.isoformat(),
                "updated_at": uo.updated_at.isoformat()
            })

        return {
            "user_orders": items,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    def cancel_my_order(self, user_order_id: str, user_id: str) -> Optional[Dict]:
        """User cancels their own order (only if ORDERED status)."""
        user_order = self.order_repo.cancel_user_order(user_order_id, user_id)
        if not user_order:
            return None

        return {
            "id": user_order.id,
            "user_id": user_order.user_id,
            "order_id": user_order.order_id,
            "status": user_order.status,
            "created_at": user_order.created_at.isoformat(),
            "updated_at": user_order.updated_at.isoformat()
        }

    def get_all_user_orders(self, page: int, page_size: int, status: Optional[str] = None) -> Dict:
        """Admin gets all user orders."""
        user_orders, total = self.order_repo.get_all_user_orders(page, page_size, status)

        items = []
        for uo in user_orders:
            order = uo.order
            user = uo.user
            items.append({
                "id": uo.id,
                "user_id": uo.user_id,
                "order_id": uo.order_id,
                "status": uo.status,
                "user_name": user.name if user else None,
                "order": {
                    "id": order.id,
                    "uuid": order.uuid,
                    "title": order.title,
                    "description": order.description,
                    "quantity": order.quantity,
                    "price": order.price,
                    "image": order.image,
                    "stock_status": order.stock_status,
                    "created_at": order.created_at.isoformat(),
                    "updated_at": order.updated_at.isoformat()
                } if order else None,
                "created_at": uo.created_at.isoformat(),
                "updated_at": uo.updated_at.isoformat()
            })

        return {
            "user_orders": items,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    def update_user_order_status(self, user_order_id: str, status: str) -> Optional[Dict]:
        """Admin updates user order status."""
        user_order = self.order_repo.update_user_order_status(user_order_id, status)
        if not user_order:
            return None

        return {
            "id": user_order.id,
            "user_id": user_order.user_id,
            "order_id": user_order.order_id,
            "status": user_order.status,
            "created_at": user_order.created_at.isoformat(),
            "updated_at": user_order.updated_at.isoformat()
        }