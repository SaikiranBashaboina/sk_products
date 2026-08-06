"""Order management API routes."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database.database import get_db
from app.schemas.order import OrderCreate, OrderUpdate, OrderStatusUpdate, StockStatusUpdate
from app.services.order_service import OrderService
from app.dependencies.auth_dependencies import get_current_user, require_admin, require_admin_or_identity, require_identity

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("")
def get_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all available orders (all authenticated users)."""
    order_service = OrderService(db)
    return order_service.get_orders(page, page_size, search)


@router.get("/{order_id}")
def get_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get order by ID."""
    order_service = OrderService(db)
    order = order_service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@router.post("", status_code=status.HTTP_201_CREATED)
def create_order(
    request: OrderCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Create a new order (Admin only)."""
    order_service = OrderService(db)
    return order_service.create_order(request.model_dump(), current_user["id"])


@router.put("/{order_id}")
def update_order(
    order_id: str,
    request: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Update an order (Admin only)."""
    order_service = OrderService(db)
    order = order_service.update_order(order_id, request.model_dump(exclude_none=True))
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@router.delete("/{order_id}")
def delete_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Delete an order (Admin only)."""
    order_service = OrderService(db)
    success = order_service.delete_order(order_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return {"message": "Order deleted successfully"}


@router.patch("/{order_id}/stock")
def update_stock_status(
    order_id: str,
    request: StockStatusUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Update order stock status (Admin only)."""
    order_service = OrderService(db)
    order = order_service.update_order(order_id, {"stock_status": request.stock_status})
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order
