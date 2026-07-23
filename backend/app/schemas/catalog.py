from pydantic import BaseModel


class CategoryItem(BaseModel):
    category_code: str
    name: str
    parent_code: str | None
    level: int
    sort_order: int


class BrandItem(BaseModel):
    brand_code: str
    name: str
    logo_url: str | None
    description: str | None
