from decimal import Decimal
from typing import Any

from neo4j.exceptions import Neo4jError
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import AppError
from app.repositories.filter_repository import FilterGraphRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.filter import FilterConditions, FilterSearchRequest
from app.services.filter_rules import ControlledFilterAnalyzer


class FilterService:
    def __init__(self, product_repository: ProductRepository, graph_repository: FilterGraphRepository, analyzer: ControlledFilterAnalyzer):
        self.product_repository = product_repository
        self.graph_repository = graph_repository
        self.analyzer = analyzer

    def analyze(self, text: str) -> dict[str, Any]:
        return self.analyzer.analyze(text).model_dump()

    def search(self, payload: FilterSearchRequest) -> dict[str, Any]:
        analyzed = self.analyzer.analyze(payload.text) if payload.text else None
        conditions = FilterConditions(
            exclude_ingredients=payload.exclude_ingredients or (analyzed.exclude_ingredients if analyzed else []),
            nutrition_targets=payload.nutrition_targets or (analyzed.nutrition_targets if analyzed else []),
            max_price=payload.max_price if payload.max_price is not None else (analyzed.max_price if analyzed else None),
            category_code=payload.category_code or (analyzed.category_code if analyzed else None),
        )
        try:
            _, products = self.product_repository.list_products({"page":1,"page_size":100,"keyword":None,"category_code":conditions.category_code,"brand_code":None,"merchant_id":None,"status":None,"sort_by":"created_at","sort_order":"desc"})
            details = {item["product_code"]: self.product_repository.get_detail(item["product_code"]) for item in products}
        except (SQLAlchemyError, RuntimeError) as exc:
            raise AppError("MYSQL_UNAVAILABLE", "Product database is unavailable", 503) from exc
        try:
            resolved = self.graph_repository.resolve_exclusions(conditions.exclude_ingredients)
        except Neo4jError as exc:
            raise AppError("NEO4J_UNAVAILABLE", "Knowledge graph is unavailable", 503) from exc
        unresolved = [term for term, rows in resolved.items() if not rows]
        code_to_term = {row["ingredient_code"]: term for term, rows in resolved.items() for row in rows}
        items = [self._classify(item, details[item["product_code"]], conditions, code_to_term, unresolved) for item in products]
        start = (payload.page - 1) * payload.page_size
        return {"total":len(items),"page":payload.page,"page_size":payload.page_size,"conditions":conditions,"items":items[start:start+payload.page_size]}

    @staticmethod
    def _classify(item: dict[str, Any], detail: dict[str, Any] | None, conditions: FilterConditions, code_to_term: dict[str, str], unresolved: list[str]) -> dict[str, Any]:
        reasons: list[str] = []
        contains_hits: list[str] = []
        may_hits: list[str] = []
        status = "MATCH"
        if detail is None:
            status, reasons = "UNKNOWN", ["商品结构化详情缺失"]
        else:
            contains_hits = sorted({code_to_term[x["entity_code"]] for x in detail["contains"] if x["entity_code"] in code_to_term})
            may_hits = sorted({code_to_term[x["entity_code"]] for x in detail["may_contain"] if x["entity_code"] in code_to_term})
            if contains_hits:
                status = "NOT_MATCH"
                reasons.append("明确含有排除成分：" + "、".join(contains_hits))
            elif may_hits:
                status = "RISK"
                reasons.append("包装提示可能含有：" + "、".join(may_hits))
            if conditions.max_price is not None:
                price = item.get("sale_price")
                if price is None and status == "MATCH": status = "UNKNOWN"
                elif price is not None and Decimal(price) > conditions.max_price:
                    status = "NOT_MATCH"; reasons.append(f"价格超过上限 {conditions.max_price} 元")
            nutrition = {x["nutrient_code"]:x for x in detail["nutrition"]}
            nutrition.update({x["nutrient_name"]:x for x in detail["nutrition"]})
            for target in conditions.nutrition_targets:
                fact = nutrition.get(target.nutrient_code) or nutrition.get(target.nutrient_name)
                if not fact or fact.get("value") is None:
                    if status == "MATCH": status = "UNKNOWN"
                    reasons.append(f"{target.nutrient_name}暂无数据")
                    continue
                value = Decimal(fact["value"])
                failed = value > target.value if target.operator == "LTE" else value < target.value
                if failed:
                    status = "NOT_MATCH"; reasons.append(f"{target.nutrient_name}{value}{fact['unit']}不符合目标")
            if unresolved and status == "MATCH":
                status = "UNKNOWN"; reasons.append("无法识别排除成分：" + "、".join(unresolved))
            if detail.get("ingredient_version") is None and status == "MATCH":
                status = "UNKNOWN"; reasons.append("结构化配料信息不足")
        if not reasons: reasons.append("满足当前已解析条件，未发现命中风险")
        return {"product_code":item["product_code"],"name":item["name"],"brand":item["brand"],"category":item["category"],"main_image_url":item.get("main_image_url"),"sale_price":item.get("sale_price"),"match_status":status,"reasons":reasons,"contains_hits":contains_hits,"may_contain_hits":may_hits}