from decimal import Decimal
from sqlalchemy.exc import SQLAlchemyError
from app.core.exceptions import AppError
class InsightService:
    def __init__(self,repository):self.repository=repository
    def recommendations(self,user_id):
        try:prefs,products=self.repository.recommendations(user_id)
        except SQLAlchemyError as exc:raise AppError("MYSQL_UNAVAILABLE","Recommendation database is unavailable",503) from exc
        excluded={x["ingredient_name"] for x in prefs if x["preference_type"]=="EXCLUDE"};preferred={x["ingredient_name"] for x in prefs if x["preference_type"]=="PREFER"};items=[]
        for p in products:
            ingredients=set((p.get("ingredients") or "").split(","));
            if ingredients & excluded:continue
            hits=sorted(ingredients & preferred); protein_preferred="高蛋白" in preferred and p.get("protein_value") is not None; score=Decimal((len(hits)+(1 if protein_preferred else 0))*10)+Decimal(p.get("favorite_count") or 0)*3+Decimal(p.get("view_count") or 0)+Decimal(p.get("purchase_count") or 0)*5;reasons=[]
            if hits:reasons.append("匹配偏好成分："+"、".join(hits))
            if protein_preferred:reasons.append("蛋白质数据符合你的高蛋白偏好")
            if p.get("purchase_count"):reasons.append("基于你的历史购买")
            elif p.get("favorite_count"):reasons.append("基于你的收藏记录")
            elif p.get("view_count"):reasons.append("基于你的浏览记录")
            if not reasons:continue
            items.append({**p,"score":score,"reasons":reasons})
        return sorted(items,key=lambda x:x["score"],reverse=True)[:12]
    def notifications(self,user_id):
        try:return self.repository.notifications(user_id)
        except SQLAlchemyError as exc:raise AppError("MYSQL_UNAVAILABLE","Notification data is unavailable",503) from exc