"""
pytest tests — run with:  pytest tests/ -v
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ─── helpers ──────────────────────────────────────────────────────────────────
def make_user(**overrides):
    base = {
        "username":  "aliza_dev",
        "email":     "aliza@example.com",
        "password":  "Secure@123",
        "full_name": "Aliza Javed",
        "age":       22,
        "role":      "viewer",
    }
    return {**base, **overrides}


def make_product(**overrides):
    base = {
        "name":        "Python Handbook",
        "description": "Complete guide to Python programming",
        "price":       "29.99",
        "discount":    10.0,
        "stock":       50,
        "category":    "books",
        "tags":        ["python", "programming"],
        "sku":         "BK-001234",
    }
    return {**base, **overrides}


# ─── Health ───────────────────────────────────────────────────────────────────
def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_health():
    r = client.get("/health")
    assert r.status_code == 200


# ─── Users ────────────────────────────────────────────────────────────────────
class TestUsers:
    def test_create_user_success(self):
        r = client.post("/api/v1/users/", json=make_user())
        assert r.status_code == 201
        body = r.json()
        assert body["username"] == "aliza_dev"
        assert "password" not in body

    def test_create_user_weak_password(self):
        r = client.post("/api/v1/users/", json=make_user(password="weakpass"))
        assert r.status_code == 422
        assert "errors" in r.json()

    def test_create_user_bad_username(self):
        r = client.post("/api/v1/users/", json=make_user(username="_bad_user_"))
        assert r.status_code == 422

    def test_create_user_invalid_email(self):
        r = client.post("/api/v1/users/", json=make_user(email="not-an-email"))
        assert r.status_code == 422

    def test_get_user_not_found(self):
        r = client.get("/api/v1/users/99999")
        assert r.status_code == 404

    def test_update_user(self):
        r = client.post("/api/v1/users/", json=make_user(
            username="update_user", email="update@example.com"
        ))
        uid = r.json()["id"]
        r2 = client.patch(f"/api/v1/users/{uid}", json={"bio": "Backend dev"})
        assert r2.status_code == 200

    def test_delete_user(self):
        r = client.post("/api/v1/users/", json=make_user(
            username="del_user", email="del@example.com"
        ))
        uid = r.json()["id"]
        r2 = client.delete(f"/api/v1/users/{uid}")
        assert r2.status_code == 204

    def test_list_users(self):
        r = client.get("/api/v1/users/?limit=5")
        assert r.status_code == 200
        assert isinstance(r.json(), list)


# ─── Products ─────────────────────────────────────────────────────────────────
class TestProducts:
    def test_create_product_success(self):
        r = client.post("/api/v1/products/", json=make_product())
        assert r.status_code == 201
        assert "final_price" in r.json()

    def test_invalid_sku(self):
        r = client.post("/api/v1/products/", json=make_product(sku="bad-sku"))
        assert r.status_code == 422

    def test_negative_price(self):
        r = client.post("/api/v1/products/", json=make_product(price="-5"))
        assert r.status_code == 422

    def test_duplicate_tags(self):
        r = client.post("/api/v1/products/",
                        json=make_product(tags=["python", "python"], sku="BK-009999"))
        assert r.status_code == 422

    def test_filter_by_category(self):
        r = client.get("/api/v1/products/?category=books")
        assert r.status_code == 200


# ─── Orders ───────────────────────────────────────────────────────────────────
class TestOrders:
    def _base_order(self):
        return {
            "user_id": 1,
            "items": [{"product_id": 1, "quantity": 2, "unit_price": "19.99"}],
            "payment_method": "card",
            "delivery_address": "123 Main Street, Islamabad, Pakistan",
        }

    def test_create_order_success(self):
        r = client.post("/api/v1/orders/", json=self._base_order())
        assert r.status_code == 201
        assert r.json()["status"] == "pending"

    def test_duplicate_products_in_order(self):
        payload = self._base_order()
        payload["items"] = [
            {"product_id": 1, "quantity": 2, "unit_price": "10.00"},
            {"product_id": 1, "quantity": 1, "unit_price": "10.00"},
        ]
        r = client.post("/api/v1/orders/", json=payload)
        assert r.status_code == 422

    def test_empty_items(self):
        payload = self._base_order()
        payload["items"] = []
        r = client.post("/api/v1/orders/", json=payload)
        assert r.status_code == 422

    def test_update_order_status(self):
        r = client.post("/api/v1/orders/", json=self._base_order())
        oid = r.json()["id"]
        r2 = client.patch(f"/api/v1/orders/{oid}/status", json={"status": "confirmed"})
        assert r2.status_code == 200
        assert r2.json()["status"] == "confirmed"

    def test_cannot_revert_to_pending(self):
        r = client.post("/api/v1/orders/", json=self._base_order())
        oid = r.json()["id"]
        r2 = client.patch(f"/api/v1/orders/{oid}/status", json={"status": "pending"})
        assert r2.status_code == 422
