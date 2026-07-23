from decimal import Decimal
from pydantic import BaseModel, Field

class CartItemCreate(BaseModel):
    product_code: str = Field(min_length=1, max_length=40)
    spec_code: str | None = Field(default=None, max_length=48)
    quantity: int = Field(default=1, gt=0, le=999)

class CartItemUpdate(BaseModel):
    quantity: int = Field(gt=0, le=999)

class CartItem(BaseModel):
    id: int
    product_code: str
    product_name: str
    spec_code: str
    spec_name: str
    image_url: str | None
    quantity: int
    unit_price: Decimal
    subtotal: Decimal
    stock_quantity: int
    sellable: bool
    selected: bool

class CartSummary(BaseModel):
    cart_code: str
    items: list[CartItem]
    item_count: int
    total_quantity: int
    total_amount: Decimal
