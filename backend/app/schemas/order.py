from datetime import datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field

OrderStatus = Literal["PENDING_PAYMENT", "PAID", "CANCELLED", "COMPLETED"]

class ReceiverSnapshot(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    phone: str = Field(min_length=6, max_length=32)
    address: str = Field(min_length=5, max_length=500)
class OrderCreate(BaseModel):
    cart_item_ids: list[int] | None = Field(default=None, max_length=100)
    receiver: ReceiverSnapshot
    buyer_remark: str | None = Field(default=None, max_length=500)

class PaymentRequest(BaseModel):
    channel: Literal["MOCK_BALANCE", "MOCK_ALIPAY", "MOCK_WECHAT"] = "MOCK_BALANCE"

class OrderItem(BaseModel):
    id: int
    product_code: str
    product_name: str
    spec_code: str
    spec_name: str
    image_url: str | None
    unit_price: Decimal
    quantity: int
    subtotal: Decimal
    ingredient_version: int | None

class OrderSummary(BaseModel):
    id: int
    order_no: str
    status: OrderStatus
    payment_status: str
    goods_amount: Decimal
    shipping_amount: Decimal
    payable_amount: Decimal
    paid_amount: Decimal
    placed_at: datetime
    paid_at: datetime | None
    items: list[OrderItem]

class OrderPage(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[OrderSummary]
