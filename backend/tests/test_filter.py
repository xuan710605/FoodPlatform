from decimal import Decimal

from app.schemas.filter import FilterSearchRequest
from app.services.filter_rules import ControlledFilterAnalyzer
from app.services.filter_service import FilterService


class ProductRepositoryStub:
    def list_products(self, _filters):
        base = {"brand":"示例品牌","category":"早餐麦片","main_image_url":None,"sale_price":Decimal("30")}
        return 3, [base|{"product_code":"FP0001","name":"安全麦片"}, base|{"product_code":"FP0002","name":"交叉接触麦片"}, base|{"product_code":"FP0017","name":"花生酱饼干"}]

    def get_detail(self, code):
        common = {"nutrition":[{"nutrient_code":"NUT_SUGAR","nutrient_name":"糖","value":Decimal("4.0"),"unit":"g"}],"ingredient_version":1}
        if code == "FP0017": return common|{"contains":[{"entity_code":"ING004"}],"may_contain":[]}
        if code == "FP0002": return common|{"contains":[],"may_contain":[{"entity_code":"ING002"}]}
        return common|{"contains":[],"may_contain":[]}


class GraphRepositoryStub:
    def resolve_exclusions(self, terms):
        return {term:[{"ingredient_code":"ING002","ingredient_name":"花生","risks":[]},{"ingredient_code":"ING004","ingredient_name":"花生酱","risks":[]}] for term in terms}


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


def test_filter_search_distinguishes_contains_and_may_contain():
    service = FilterService(ProductRepositoryStub(), GraphRepositoryStub(), ControlledFilterAnalyzer())
    result = service.search(FilterSearchRequest(exclude_ingredients=["花生"]))
    statuses = {item["product_code"]:item["match_status"] for item in result["items"]}
    assert statuses == {"FP0001":"MATCH","FP0002":"RISK","FP0017":"NOT_MATCH"}