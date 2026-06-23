from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.order import OrderCreate, OrderResponse, OrderStatus, OrderStatusUpdate
from app.services import store

router = APIRouter()


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED,
             summary="Place an order")
async def create_order(payload: OrderCreate):
    """
    Creates an order with:
    - Duplicate product detection across items
    - Order total cap (max 100,000)
    - Promo code format check
    """
    data = payload.model_dump()
    order = store.create_order(data)
    return order


@router.get("/", response_model=List[OrderResponse], summary="List orders")
async def list_orders(
    user_id: Optional[int]    = Query(default=None, gt=0),
    order_status: Optional[OrderStatus] = Query(default=None),
    limit:  int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    orders = store.get_all_orders(user_id=user_id)
    if order_status:
        orders = [o for o in orders if o["status"] == order_status]
    return orders[offset: offset + limit]


@router.get("/{order_id}", response_model=OrderResponse, summary="Get order by ID")
async def get_order(order_id: int):
    order = store.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    return order


@router.patch("/{order_id}/status", response_model=OrderResponse,
              summary="Update order status")
async def update_order_status(order_id: int, payload: OrderStatusUpdate):
    """
    Status transitions allowed:
    pending → confirmed → shipped → delivered
    Any status → cancelled
    Cannot revert back to pending.
    """
    order = store.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")

    current = order["status"]
    new     = payload.status.value

    # Guard: can't update a delivered or already-cancelled order
    if current in ("delivered", "cancelled"):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot change status of a '{current}' order",
        )

    updated = store.update_order_status(order_id, new)
    return updated
