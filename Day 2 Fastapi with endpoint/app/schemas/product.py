from decimal import Decimal
from enum import Enum
from typing import Annotated, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class Category(str, Enum):
    electronics = "electronics"
    clothing    = "clothing"
    books       = "books"
    food        = "food"
    other       = "other"


Price = Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]


class ProductCreate(BaseModel):
    name:        str      = Field(..., min_length=2, max_length=200, examples=["Python Book"])
    description: str      = Field(..., min_length=10, max_length=2000)
    price:       Price    = Field(..., examples=[29.99])
    discount:    float    = Field(default=0.0, ge=0.0, le=100.0,
                                  description="Discount percentage 0–100")
    stock:       int      = Field(..., ge=0, examples=[50])
    category:    Category = Field(..., examples=[Category.books])
    tags:        List[str] = Field(default_factory=list, max_length=10)
    sku:         str      = Field(..., pattern=r"^[A-Z]{2,4}-\d{4,8}$",
                                  examples=["BK-001234"], description="Format: XX-0000")

    @field_validator("name")
    @classmethod
    def name_no_special_chars(cls, v: str) -> str:
        allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -_&'.")
        illegal = set(v) - allowed
        if illegal:
            raise ValueError(f"Name contains invalid characters: {illegal}")
        return v.strip()

    @field_validator("tags")
    @classmethod
    def tags_lowercase(cls, v: List[str]) -> List[str]:
        cleaned = [tag.strip().lower() for tag in v if tag.strip()]
        if len(cleaned) != len(set(cleaned)):
            raise ValueError("Duplicate tags are not allowed")
        return cleaned

    @model_validator(mode="after")
    def stock_zero_when_discontinued(self) -> "ProductCreate":
        # If price is suspiciously high and stock is 0 it's likely discontinued
        # Just an example of cross-field logic
        if self.stock == 0 and self.discount > 50:
            raise ValueError("Heavily discounted items cannot have zero stock")
        return self

    @property
    def final_price(self) -> Decimal:
        return self.price * Decimal(str(1 - self.discount / 100))


class ProductUpdate(BaseModel):
    name:        Optional[str]      = Field(default=None, min_length=2, max_length=200)
    description: Optional[str]      = Field(default=None, min_length=10, max_length=2000)
    price:       Optional[Price]    = None
    discount:    Optional[float]    = Field(default=None, ge=0.0, le=100.0)
    stock:       Optional[int]      = Field(default=None, ge=0)
    tags:        Optional[List[str]] = None


class ProductResponse(BaseModel):
    id:          int
    name:        str
    description: str
    price:       Decimal
    discount:    float
    final_price: Decimal
    stock:       int
    category:    Category
    tags:        List[str]
    sku:         str

    model_config = {"from_attributes": True}
