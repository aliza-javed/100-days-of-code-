# Day 2 — FastAPI with Advanced Pydantic Validation

Part of my [#100DaysOfCode](../100-days-of-code.md) challenge.

A production-structured REST API with **three resource domains** (Users, Products, Orders),
each backed by advanced Pydantic v2 validation, custom error responses, and 20 passing tests.

## What's inside

```
app/
├── main.py                        # FastAPI app, CORS, custom 422 handler
├── core/config.py                 # pydantic-settings config
├── schemas/
│   ├── user.py                    # UserCreate / UserUpdate / UserResponse
│   ├── product.py                 # ProductCreate / ProductUpdate / ProductResponse
│   └── order.py                   # OrderCreate / OrderStatusUpdate / OrderResponse
├── services/store.py              # in-memory data store (swap for ORM later)
└── api/v1/endpoints/
    ├── users.py                   # GET/POST/PATCH/DELETE /api/v1/users
    ├── products.py                # GET/POST/PATCH/DELETE /api/v1/products
    └── orders.py                  # GET/POST/PATCH        /api/v1/orders
tests/
└── test_api.py                    # 20 pytest tests (all passing)
```

## Pydantic features used

| Feature | Where |
|---|---|
| `@field_validator` | Password strength, username format, tag deduplication |
| `@model_validator` | Age ↔ date-of-birth cross-check, order total cap |
| `Annotated` + `Field` | Reusable `Price` type with `gt`, `max_digits`, `decimal_places` |
| `Enum` fields | `UserRole`, `Category`, `OrderStatus`, `PaymentMethod` |
| Nested models | `Address` inside `UserCreate` |
| `pattern=` regex | SKU format `BK-001234`, promo code |
| Custom 422 handler | Clean `{field, message, type}` error format |
| `exclude_unset=True` | Partial PATCH — only update provided fields |

## Quick start

```bash
# 1. clone & install
git clone https://github.com/aliza-javed/100-days-of-code.git
cd 100-days-of-code/day02-fastapi
pip install -r requirements.txt

# 2. run
uvicorn app.main:app --reload

# 3. test
pytest tests/ -v
```

Open **http://localhost:8000/docs** for the interactive Swagger UI.

## Endpoints

### Users  `/api/v1/users`
| Method | Path | Description |
|--------|------|-------------|
| POST | `/` | Create user (full validation) |
| GET | `/` | List users (filter by role, pagination) |
| GET | `/{id}` | Get user |
| PATCH | `/{id}` | Partial update |
| DELETE | `/{id}` | Delete user |

### Products  `/api/v1/products`
| Method | Path | Description |
|--------|------|-------------|
| POST | `/` | Create product (SKU check, tag dedup) |
| GET | `/` | List (filter by category, price, stock) |
| GET | `/{id}` | Get product |
| PATCH | `/{id}` | Partial update |
| DELETE | `/{id}` | Delete product |

### Orders  `/api/v1/orders`
| Method | Path | Description |
|--------|------|-------------|
| POST | `/` | Place order (duplicate item check, total cap) |
| GET | `/` | List (filter by user, status) |
| GET | `/{id}` | Get order |
| PATCH | `/{id}/status` | Update status (guarded transitions) |

## Tech stack

- **FastAPI** 0.115
- **Pydantic v2** with `pydantic-settings`
- **pytest** + **httpx** TestClient
- Python 3.12

## What I learned today

- `@model_validator(mode="after")` runs after all field validators — perfect for cross-field logic
- `Annotated` types let you define reusable constrained types (like `Price`) once and reuse them
- `exclude_unset=True` on `.model_dump()` is essential for PATCH endpoints
- Custom `RequestValidationError` handler makes 422 errors much friendlier
