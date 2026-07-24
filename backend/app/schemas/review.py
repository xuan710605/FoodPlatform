from datetime import datetime
from pydantic import BaseModel, Field

class ReviewCreate(BaseModel):
    order_item_id: int = Field(gt=0)
    rating: int = Field(ge=1, le=5)
    review_text: str | None = Field(default=None, max_length=2000)

class ReviewItem(BaseModel):
    id: int
    review_code: str
    order_item_id: int | None
    product_code: str
    product_name: str
    username: str
    rating: int
    review_text: str | None
    reviewed_at: datetime

class ReviewPage(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[ReviewItem]