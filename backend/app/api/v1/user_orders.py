"""User order management API routes."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database.database import get_db
from app.schemas.order import OrderStatusUpdate
from app.services.order_service import OrderService
from app.dependencies.auth_dependencies import get_current_user, require_admin

router = APIRouter(prefix="/orders", tags=["User Orders"])


@router.post("/{order_id}/select")
def select_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """User selects/orders an item."""
    order_service = OrderService(db)
    try:
        result = order_service.select_order(current_user["id"], order_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    return result


@router.get("/my/list")
def get_my_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get current user's orders."""
    order_service = OrderService(db)
    return order_service.get_my_orders(current_user["id"], page, page_size)


@router.patch("/my/{user_order_id}/cancel")
def cancel_my_order(
    user_order_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Cancel own order (only if ORDERED status)."""
    order_service = OrderService(db)
    result = order_service.cancel_my_order(user_order_id, current_user["id"])
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order cannot be cancelled or not found"
        )
    return result


@router.get("/admin/all")
def get_all_user_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Admin gets all user orders."""
    order_service = OrderService(db)
    return order_service.get_all_user_orders(page, page_size, status_filter)


@router.patch("/admin/{user_order_id}/status")
def update_order_status(
    user_order_id: str,
    request: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Admin updates order status."""
    order_service = OrderService(db)
    result = order_service.update_user_order_status(user_order_id, request.status)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User order not found")
    return result