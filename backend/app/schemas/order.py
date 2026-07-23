from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, Field

OrderStatus = Literal["PENDING_PAYMENT", "PAID", "SHIPPING", "CANCELLED", "COMPLETED"]


class OrderCreate(BaseModel):
    cart_item_ids: list[int] | None = Field(default=None, max_length=100)
    address_code: str = Field(min_length=1, max_length=40)
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
    receiver_snapshot: dict[str, Any] | None = None
    goods_amount: Decimal
    shipping_amount: Decimal
    payable_amount: Decimal
    paid_amount: Decimal
    placed_at: datetime
    paid_at: datetime | None
    shipped_at: datetime | None = None
    completed_at: datetime | None = None
    cancelled_at: datetime | None = None
    cancel_reason: str | None = None
    buyer_remark: str | None = None
    items: list[OrderItem]


class OrderPage(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[OrderSummary]
