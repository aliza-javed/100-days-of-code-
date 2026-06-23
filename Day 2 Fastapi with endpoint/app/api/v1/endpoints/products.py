from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.product import Category, ProductCreate, ProductResponse, ProductUpdate
from app.services import store

router = APIRouter()


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED,
             summary="Create a product")
async def create_product(payload: ProductCreate):
    """
    Creates a product with:
    - SKU format validation  (e.g. BK-001234)
    - Tag deduplication
    - Cross-field: heavily discounted items must have stock > 0
    """
    existing = [p for p in store.get_all_products() if p["sku"] == payload.sku]
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"SKU '{payload.sku}' already exists",
        )
    product = store.create_product(payload.model_dump())
    return product


@router.get("/", response_model=List[ProductResponse], summary="List / filter products")
async def list_products(
    category: Optional[Category] = Query(default=None),
    min_price: Optional[float]   = Query(default=None, gt=0),
    max_price: Optional[float]   = Query(default=None, gt=0),
    in_stock:  bool              = Query(default=False),
    limit: int  = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    products = store.get_all_products(category=category.value if category else None)
    if min_price is not None:
        products = [p for p in products if float(p["price"]) >= min_price]
    if max_price is not None:
        products = [p for p in products if float(p["price"]) <= max_price]
    if in_stock:
        products = [p for p in products if p["stock"] > 0]
    return products[offset: offset + limit]


@router.get("/{product_id}", response_model=ProductResponse, summary="Get product by ID")
async def get_product(product_id: int):
    product = store.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    return product


@router.patch("/{product_id}", response_model=ProductResponse,
              summary="Partial update a product")
async def update_product(product_id: int, payload: ProductUpdate):
    updated = store.update_product(product_id, payload.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    return updated


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete a product")
async def delete_product(product_id: int):
    if not store.delete_product(product_id):
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
