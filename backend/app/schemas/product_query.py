from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field

class ProductQuery(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    keyword: str | None = Field(default=None, max_length=100)
    category: str | None = Field(default=None, max_length=100)
    category_code: str | None = Field(default=None, max_length=32)
    brand: str | None = Field(default=None, max_length=100)
    brand_code: str | None = Field(default=None, max_length=32)
    excluded_ingredients: list[str] = Field(default_factory=list, max_length=20)
    sugar_max: Decimal | None = Field(default=None, ge=0)
    fat_max: Decimal | None = Field(default=None, ge=0)
    protein_min: Decimal | None = Field(default=None, ge=0)
    sodium_max: Decimal | None = Field(default=None, ge=0)
    price_min: Decimal | None = Field(default=None, ge=0)
    price_max: Decimal | None = Field(default=None, ge=0)
    merchant_id: int | None = Field(default=None, gt=0)
    status: Literal['ON_SALE','OFF_SALE','SUSPENDED'] | None = None
    sort_by: Literal['created_at','updated_at','name','price','stock'] = 'created_at'
    sort_order: Literal['asc','desc'] = 'desc'

class CategoryProductCount(BaseModel):
    category_code: str
    category_name: str
    product_count: int
