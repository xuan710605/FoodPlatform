from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
class RecommendationItem(BaseModel):
    product_code:str; name:str; brand:str; image_url:str|None; sale_price:Decimal|None; score:Decimal; reasons:list[str]
class NotificationItem(BaseModel):
    id:str; type:str; title:str; message:str; created_at:datetime; target_path:str|None=None