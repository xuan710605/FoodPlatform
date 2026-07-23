from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

class FavoriteCreate(BaseModel):
    product_code: str = Field(min_length=1, max_length=40)

class FavoriteItem(BaseModel):
    id: int
    product_id: int
    product_code: str
    name: str
    brand: str
    category: str
    main_image_url: str | None
    sale_price: Decimal | None
    sale_status: str
    audit_status: str
    created_at: datetime
