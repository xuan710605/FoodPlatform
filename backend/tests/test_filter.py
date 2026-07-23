from decimal import Decimal

from app.schemas.filter import FilterSearchRequest
from app.services.filter_rules import ControlledFilterAnalyzer
from app.services.filter_service import FilterService


class ProductRepositoryStub:
    products = [
        {"product_code":"FP0001","name":"安全麦片","brand":"示例品牌","category":"早餐麦片","category_code":"CAT001","main_image_url":None,"sale_price":Decimal("30")},
        {"product_code":"FP0002","name":"交叉接触麦片","brand":"示例品牌","category":"早餐麦片","category_code":"CAT001","main_image_url":None,"sale_price":Decimal("30")},
        {"product_code":"FP0017","name":"花生酱饼干","brand":"示例品牌","category":"早餐麦片","category_code":"CAT001","main_image_url":None,"sale_price":Decimal("30")},
        {"product_code":"FP0004","name":"有机全脂鲜牛奶","brand":"牧场清晨","category":"乳品酸奶","category_code":"CAT003","main_image_url":None,"sale_price":Decimal("59.9")},
    ]

    def list_products(self, filters):
        items = [item for item in self.products if not filters.get("category_code") or item["category_code"] == filters["category_code"]]
        return len(items), items

    def get_detail(self, code):
        common = {
            "nutrition":[
                {"nutrient_code":"NUT_SUGAR","nutrient_name":"糖","value":Decimal("4.0"),"unit":"g"},
                {"nutrient_code":"NUT_PROTEIN","nutrient_name":"蛋白质","value":Decimal("9.0"),"unit":"g"},
            ],
            "ingredient_version":1,
        }
        if code == "FP0017": return common|{"contains":[{"entity_code":"ING004"}],"may_contain":[]}
        if code == "FP0002": return common|{"contains":[],"may_contain":[{"entity_code":"ING002"}]}
        return common|{"contains":[],"may_contain":[]}


class GraphRepositoryStub:
    def resolve_exclusions(self, terms):
        return {term:[{"ingredient_code":"ING002","ingredient_name":"花生","risks":[]},{"ingredient_code":"ING004","ingredient_name":"花生酱","risks":[]}] for term in terms}


def filter_service():
    return FilterService(ProductRepositoryStub(), GraphRepositoryStub(), ControlledFilterAnalyzer())


def test_filter_analyze_controlled_rules(client):
    response = client.post("/api/v1/filter/analyze", json={"text":"帮我找不含花生、50元以内的低糖早餐麦片"})
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["exclude_ingredients"] == ["花生"]
    assert data["max_price"] == "50"
    assert data["category_code"] == "CAT001"
    assert data["nutrition_targets"][0]["nutrient_code"] == "NUT_SUGAR"
    assert data["parser"] == "CONTROLLED_RULES"


def test_filter_search_http_contract(client):
    response = client.post("/api/v1/filter/search", json={"exclude_ingredients":["花生"]})
    assert response.status_code == 200
    assert response.json()["data"]["items"][0]["match_status"] == "MATCH"


def test_milk_query_returns_only_dairy_products():
    result = filter_service().search(FilterSearchRequest(text="牛奶"))
    assert {item["product_code"] for item in result["items"]} == {"FP0004"}
    assert {item["category"] for item in result["items"]} == {"乳品酸奶"}


def test_breakfast_cereal_query_returns_only_grain_products():
    result = filter_service().search(FilterSearchRequest(text="早餐麦片"))
    assert result["items"]
    assert {item["category"] for item in result["items"]} == {"早餐麦片"}
    assert "FP0004" not in {item["product_code"] for item in result["items"]}


def test_excluding_peanut_keeps_risk_products_out_of_matches():
    result = filter_service().search(FilterSearchRequest(exclude_ingredients=["花生"]))
    statuses = {item["product_code"]:item["match_status"] for item in result["items"]}
    assert statuses["FP0001"] == "MATCH"
    assert statuses["FP0002"] == "RISK"
    assert statuses["FP0017"] == "NOT_MATCH"
    assert {code for code,status in statuses.items() if status == "MATCH"}.isdisjoint({"FP0002","FP0017"})