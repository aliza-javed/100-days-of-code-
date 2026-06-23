"""
In-memory store — replaces a real DB for this demo.
In production: swap these functions with SQLAlchemy/Tortoise ORM calls.
"""
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

# ---------- fake stores ----------
_users: Dict[int, dict]    = {}
_products: Dict[int, dict] = {}
_orders: Dict[int, dict]   = {}
_counters = {"user": 0, "product": 0, "order": 0}


def _next_id(resource: str) -> int:
    _counters[resource] += 1
    return _counters[resource]


# ---------- Users ----------
def create_user(data: dict) -> dict:
    uid = _next_id("user")
    record = {**data, "id": uid, "created_at": datetime.utcnow()}
    record.pop("password", None)          # never store plain password
    _users[uid] = record
    return record


def get_user(uid: int) -> Optional[dict]:
    return _users.get(uid)


def get_all_users() -> List[dict]:
    return list(_users.values())


def update_user(uid: int, data: dict) -> Optional[dict]:
    if uid not in _users:
        return None
    _users[uid].update({k: v for k, v in data.items() if v is not None})
    return _users[uid]


def delete_user(uid: int) -> bool:
    if uid in _users:
        del _users[uid]
        return True
    return False


# ---------- Products ----------
def create_product(data: dict) -> dict:
    pid  = _next_id("product")
    price    = data["price"]
    discount = data.get("discount", 0.0)
    final    = price * Decimal(str(1 - discount / 100))
    record   = {**data, "id": pid, "final_price": round(final, 2)}
    _products[pid] = record
    return record


def get_product(pid: int) -> Optional[dict]:
    return _products.get(pid)


def get_all_products(category: Optional[str] = None) -> List[dict]:
    products = list(_products.values())
    if category:
        products = [p for p in products if p["category"] == category]
    return products


def update_product(pid: int, data: dict) -> Optional[dict]:
    if pid not in _products:
        return None
    _products[pid].update({k: v for k, v in data.items() if v is not None})
    price    = _products[pid]["price"]
    discount = _products[pid].get("discount", 0.0)
    _products[pid]["final_price"] = round(price * Decimal(str(1 - discount / 100)), 2)
    return _products[pid]


def delete_product(pid: int) -> bool:
    if pid in _products:
        del _products[pid]
        return True
    return False


# ---------- Orders ----------
def create_order(data: dict) -> dict:
    oid   = _next_id("order")
    items = data["items"]
    total = sum(
        item["unit_price"] * item["quantity"] for item in items
    )
    record = {**data, "id": oid, "total": round(total, 2), "status": "pending"}
    _orders[oid] = record
    return record


def get_order(oid: int) -> Optional[dict]:
    return _orders.get(oid)


def get_all_orders(user_id: Optional[int] = None) -> List[dict]:
    orders = list(_orders.values())
    if user_id:
        orders = [o for o in orders if o["user_id"] == user_id]
    return orders


def update_order_status(oid: int, status: str) -> Optional[dict]:
    if oid not in _orders:
        return None
    _orders[oid]["status"] = status
    return _orders[oid]
