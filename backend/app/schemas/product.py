from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class MoneyModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    @field_serializer("*", when_used="json", check_fields=False)
    def serialize_decimal(self, value: object) -> object:
        return format(value, "f") if isinstance(value, Decimal) else value


class ProductListItem(MoneyModel):
    id: int
    product_code: str
    name: str
    subtitle: str | None
    brand: str
    brand_code: str
    category: str
    category_code: str
    merchant: str
    merchant_id: int
    main_image_url: str | None
    sale_price: Decimal | None
    market_price: Decimal | None
    stock_quantity: int | None
    sellable: bool | None
    audit_status: str
    sale_status: str
    ingredient_version: int | None
    created_at: datetime
    updated_at: datetime


class ProductSpec(MoneyModel):
    spec_code: str
    spec_name: str
    unit_name: str
    net_content_value: Decimal | None
    net_content_unit: str | None
    is_default: bool
    sale_price: Decimal | None
    market_price: Decimal | None
    currency: str | None
    stock_quantity: int | None
    sellable: bool | None


class ProductImage(BaseModel):
    image_type: str
    image_url: str
    alt_text: str | None
    sort_order: int


class NutritionItem(MoneyModel):
    nutrient_code: str
    nutrient_name: str
    value: Decimal | None
    unit: str
    basis: str
    basis_quantity: Decimal
    source_code: str


class IngredientSummary(MoneyModel):
    entity_code: str
    name: str
    entity_type: str
    relation_type: str
    confidence: Decimal | None
    source_code: str
    audit_status: str


class MerchantPublic(BaseModel):
    merchant_code: str
    name: str


class ProductDetail(MoneyModel):
    id: int
    product_code: str
    name: str
    subtitle: str | None
    description: str | None
    brand: str
    brand_code: str
    category: str
    category_code: str
    merchant: MerchantPublic
    raw_ingredient_text: str
    allergen_notice: str | None
    ingredient_version: int | None
    graph_sync_status: str
    specs: list[ProductSpec]
    images: list[ProductImage]
    nutrition: list[NutritionItem]
    contains: list[IngredientSummary]
    may_contain: list[IngredientSummary]
    unknown: list[IngredientSummary]
    sales_quantity: int
    average_rating: Decimal | None
    review_count: int
    match_status: str
    match_reason: str | None
    evidence_text: str | None
    info_source: str | None
    audit_status: str
    sale_status: str
    created_at: datetime
    updated_at: datetime
