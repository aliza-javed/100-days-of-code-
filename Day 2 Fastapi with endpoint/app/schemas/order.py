from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class OrderStatus(str, Enum):
    pending    = "pending"
    confirmed  = "confirmed"
    shipped    = "shipped"
    delivered  = "delivered"
    cancelled  = "cancelled"


class PaymentMethod(str, Enum):
    card        = "card"
    cash        = "cash"
    bank_transfer = "bank_transfer"


class OrderItem(BaseModel):
    product_id: int   = Field(..., gt=0)
    quantity:   int   = Field(..., gt=0, le=100)
    unit_price: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)

    @property
    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity


class OrderCreate(BaseModel):
    user_id:        int           = Field(..., gt=0)
    items:          List[OrderItem] = Field(..., min_length=1, max_length=50)
    payment_method: PaymentMethod
    delivery_address: str         = Field(..., min_length=10, max_length=500)
    notes:          Optional[str] = Field(default=None, max_length=300)
    promo_code:     Optional[str] = Field(default=None, pattern=r"^[A-Z0-9]{4,12}$")

    @field_validator("items")
    @classmethod
    def no_duplicate_products(cls, v: List[OrderItem]) -> List[OrderItem]:
        product_ids = [item.product_id for item in v]
        if len(product_ids) != len(set(product_ids)):
            raise ValueError("Duplicate products in order — increase quantity instead")
        return v

    @model_validator(mode="after")
    def validate_order_total(self) -> "OrderCreate":
        total = sum(item.subtotal for item in self.items)
        if total > Decimal("100000"):
            raise ValueError("Single order total cannot exceed 100,000. Split into multiple orders.")
        return self

    @property
    def total(self) -> Decimal:
        return sum(item.subtotal for item in self.items)


class OrderStatusUpdate(BaseModel):
    status: OrderStatus

    @field_validator("status")
    @classmethod
    def cannot_reopen(cls, v: OrderStatus) -> OrderStatus:
        if v == OrderStatus.pending:
            raise ValueError("Cannot revert an order back to 'pending'")
        return v


class OrderResponse(BaseModel):
    id:               int
    user_id:          int
    items:            List[OrderItem]
    total:            Decimal
    status:           OrderStatus
    payment_method:   PaymentMethod
    delivery_address: str

    model_config = {"from_attributes": True}
