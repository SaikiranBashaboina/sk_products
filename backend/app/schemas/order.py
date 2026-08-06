"""Pydantic schemas for Order."""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator


class OrderBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)
    image: Optional[str] = None
    stock_status: str = Field(default="IN_STOCK", pattern="^(IN_STOCK|OUT_OF_STOCK)$")


class OrderCreate(OrderBase):
    pass


class StockStatusUpdate(BaseModel):
    stock_status: str = Field(..., pattern="^(IN_STOCK|OUT_OF_STOCK)$")


class OrderUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    quantity: Optional[int] = Field(None, gt=0)
    price: Optional[float] = Field(None, gt=0)
    image: Optional[str] = None


class OrderResponse(OrderBase):
    id: str
    uuid: str
    created_by_admin: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    orders: List[OrderResponse]
    total: int
    page: int
    page_size: int


class UserOrderResponse(BaseModel):
    id: str
    user_id: str
    order_id: str
    status: str
    order: Optional[OrderResponse] = None
    user_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserOrderListResponse(BaseModel):
    user_orders: List[UserOrderResponse]
    total: int
    page: int
    page_size: int


class OrderStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(ORDERED|PROCESSED|DELIVERED|CANCELLED)$")