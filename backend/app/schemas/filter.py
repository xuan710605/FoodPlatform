from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.core.filter_categories import normalize_category_code, normalize_category_codes


class NutritionTarget(BaseModel):
    nutrient_code: str | None = Field(default=None, max_length=40)
    nutrient_name: str = Field(min_length=1, max_length=120)
    operator: Literal["LTE", "GTE"]
    value: Decimal = Field(ge=0)
    unit: str = Field(min_length=1, max_length=24)
    basis: Literal["PER_100G", "PER_100ML"] = "PER_100G"


class FilterAnalyzeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=500)


class FilterConditions(BaseModel):
    exclude_ingredients: list[str] = Field(default_factory=list, max_length=20)
    exclude_categories: list[str] = Field(default_factory=list, max_length=10)
    preferred_ingredients: list[str] = Field(default_factory=list, max_length=20)
    nutrition_targets: list[NutritionTarget] = Field(default_factory=list, max_length=10)
    max_price: Decimal | None = Field(default=None, ge=0)
    category_code: str | None = Field(default=None, max_length=32)

    @field_validator("exclude_categories", mode="before")
    @classmethod
    def normalize_excluded_categories(cls, value: object) -> object:
        if value is None:
            return []
        if not isinstance(value, list):
            return value
        return normalize_category_codes(value)

    @field_validator("category_code", mode="before")
    @classmethod
    def normalize_selected_category(cls, value: object) -> object:
        if value is None or not isinstance(value, str):
            return value
        return normalize_category_code(value)


class FilterAnalyzeResult(FilterConditions):
    normalized_text: str
    parser: Literal["CONTROLLED_RULES", "QWEN_MERGED", "CONTROLLED_RULES_FALLBACK"] = "CONTROLLED_RULES"
    qwen_used: bool = False
    fallback_reason: str | None = None
    unparsed_fragments: list[str] = Field(default_factory=list)


class FilterSearchRequest(FilterConditions):
    text: str | None = Field(default=None, min_length=1, max_length=500)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

class FilterReason(BaseModel):
    source: Literal["exclude", "nutrition", "price", "unknown", "preference", "match"]
    message: str

class FilterProductItem(BaseModel):
    product_code: str
    name: str
    brand: str
    category: str
    main_image_url: str | None
    sale_price: Decimal | None
    match_status: Literal["MATCH", "RISK", "NOT_MATCH", "UNKNOWN"]
    reason: str
    reason_source: Literal["exclude", "nutrition", "price", "unknown", "preference", "match"]
    reasons: list[str]
    reason_details: list[FilterReason]
    contains_hits: list[str]
    may_contain_hits: list[str]
    preference_hits: list[str]


class FilterSearchResult(BaseModel):
    total: int
    page: int
    page_size: int
    conditions: FilterConditions
    items: list[FilterProductItem]
