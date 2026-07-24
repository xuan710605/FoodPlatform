from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.product import MoneyModel


class MerchantDashboard(MoneyModel):
    merchant_code: str
    merchant_name: str
    product_count: int
    on_sale_count: int
    pending_review_count: int
    order_count: int
    paid_order_count: int
    sales_amount: Decimal


class MerchantProductItem(MoneyModel):
    product_code: str
    name: str
    subtitle: str | None
    description: str | None
    raw_ingredient_text: str
    allergen_notice: str | None
    brand: str
    brand_code: str
    category: str
    category_code: str
    spec_name: str
    unit_name: str
    image_url: str | None
    sale_status: str
    review_status: str
    sale_price: Decimal | None
    stock_quantity: int | None
    updated_at: datetime


class MerchantProductWrite(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    subtitle: str | None = Field(default=None, max_length=255)
    description: str | None = None
    brand_code: str = Field(min_length=1, max_length=32)
    category_code: str = Field(min_length=1, max_length=32)
    raw_ingredient_text: str = Field(min_length=1)
    allergen_notice: str | None = None
    spec_name: str = Field(min_length=1, max_length=160)
    unit_name: str = Field(default="件", min_length=1, max_length=32)
    price: Decimal = Field(ge=0)
    stock_quantity: int = Field(default=0, ge=0)
    image_url: str | None = Field(default=None, max_length=1024)


class SaleStatusUpdate(BaseModel):
    sale_status: Literal["ON_SALE", "OFF_SALE"]


class MerchantOrderItem(MoneyModel):
    id: int
    order_no: str
    buyer: str
    status: Literal["PENDING_PAYMENT", "PAID", "SHIPPING", "COMPLETED", "CANCELLED", "REFUND_REQUESTED"]
    payable_amount: Decimal
    paid_amount: Decimal
    item_count: int
    placed_at: datetime
    paid_at: datetime | None
    shipped_at: datetime | None
    completed_at: datetime | None


class MerchantOrderStatusUpdate(BaseModel):
    status: Literal["SHIPPING", "COMPLETED"]


class AdminDashboard(BaseModel):
    user_count: int
    merchant_count: int
    product_count: int
    pending_product_count: int
    order_count: int


class AdminUserItem(BaseModel):
    id: int
    user_code: str
    username: str
    email: str | None
    user_type: str
    status: str
    roles: list[str]
    created_at: datetime


class AdminUserStatusUpdate(BaseModel):
    status: Literal["ACTIVE", "DISABLED"]


class AdminProductItem(BaseModel):
    product_code: str
    name: str
    merchant_code: str
    merchant_name: str
    brand: str
    category: str
    review_status: str
    sale_status: str
    submitted_at: datetime | None
    updated_at: datetime


class ProductApproval(BaseModel):
    opinion: str | None = Field(default=None, max_length=1000)