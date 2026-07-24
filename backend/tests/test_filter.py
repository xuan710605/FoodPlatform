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
        {"product_code":"FP0008","name":"全麦核桃软欧包","brand":"麦香工房","category":"面包烘焙","category_code":"CAT006","main_image_url":None,"sale_price":Decimal("22.8")},
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
        if code == "FP0017":
            common["nutrition"][0]["value"] = Decimal("12.0")
            return common|{"contains":[{"entity_code":"ING004","name":"花生酱"}],"may_contain":[]}
        if code == "FP0002": return common|{"contains":[],"may_contain":[{"entity_code":"ING002","name":"花生"}]}
        return common|{"contains":[{"entity_code":"ING001","name":"燕麦"}] if code == "FP0001" else [],"may_contain":[]}


class GraphRepositoryStub:
    def resolve_exclusions(self, terms):
        return {term:[{"ingredient_code":"ING002","ingredient_name":"花生","risks":[]},{"ingredient_code":"ING004","ingredient_name":"花生酱","risks":[]}] for term in terms}


def filter_service():
    return FilterService(ProductRepositoryStub(), GraphRepositoryStub(), ControlledFilterAnalyzer())


def test_filter_analyze_controlled_rules(client):
    response = client.post("/api/v1/filter/analyze", json={"text":"帮我找不含花生、50元以内、糖不超过5g的早餐麦片"})
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

def test_negated_juice_is_an_excluded_category(client):
    response = client.post("/api/v1/filter/analyze", json={"text": "不含果汁"})
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["category_code"] is None
    assert data["exclude_categories"] == ["CAT005"]


def test_negated_peanut_keeps_positive_breakfast_category(client):
    response = client.post("/api/v1/filter/analyze", json={"text": "不要花生的早餐"})
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["exclude_ingredients"] == ["花生"]
    assert data["exclude_categories"] == []
    assert data["category_code"] == "CAT001"


def test_high_protein_milk_is_positive_dairy_query(client):
    response = client.post("/api/v1/filter/analyze", json={"text": "高蛋白牛奶"})
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["category_code"] == "CAT003"
    assert data["exclude_ingredients"] == []
    assert data["exclude_categories"] == []
    assert data["nutrition_targets"] == []
    assert data["preferred_ingredients"] == ["高蛋白"]


def test_excluded_category_is_removed_from_search_results():
    result = filter_service().search(FilterSearchRequest(exclude_categories=["CAT003"]))
    assert "FP0004" not in {item["product_code"] for item in result["items"]}

class PreferenceRepositoryStub:
    def get_food_preferences(self, user_id):
        if user_id == 1:
            return {"exclude_ingredients": ["花生"], "preferred_ingredients": ["燕麦"]}
        return {"exclude_ingredients": [], "preferred_ingredients": []}


def test_saved_exclusions_are_isolated_and_raise_peanut_risk():
    service = FilterService(ProductRepositoryStub(), GraphRepositoryStub(), ControlledFilterAnalyzer(), PreferenceRepositoryStub())
    user_a = service.search(FilterSearchRequest(text="早餐麦片"), user_id=1)
    user_b = service.search(FilterSearchRequest(text="早餐麦片"), user_id=2)
    statuses_a = {item["product_code"]: item["match_status"] for item in user_a["items"]}
    statuses_b = {item["product_code"]: item["match_status"] for item in user_b["items"]}
    assert statuses_a["FP0017"] == "NOT_MATCH"
    assert statuses_a["FP0002"] == "RISK"
    assert statuses_b["FP0017"] == "MATCH"
    assert user_a["conditions"].exclude_ingredients == ["花生"]
    assert user_b["conditions"].exclude_ingredients == []


def test_saved_preferred_ingredient_affects_order_without_overriding_manual_conditions():
    service = FilterService(ProductRepositoryStub(), GraphRepositoryStub(), ControlledFilterAnalyzer(), PreferenceRepositoryStub())
    result = service.search(FilterSearchRequest(text="早餐麦片", exclude_ingredients=["芝麻"]), user_id=1)
    assert result["conditions"].exclude_ingredients == ["芝麻", "花生"]
    assert result["items"][0]["product_code"] == "FP0001"
    assert result["items"][0]["preference_hits"] == ["燕麦"]

def test_product_facts_do_not_create_not_match_without_user_exclusions():
    result = filter_service().search(FilterSearchRequest())
    statuses = {item["product_code"]: item["match_status"] for item in result["items"]}
    assert statuses["FP0017"] == "MATCH"
    assert statuses["FP0002"] == "MATCH"
    assert result["conditions"].exclude_ingredients == []


def test_exclusion_reason_is_transparent():
    result = filter_service().search(FilterSearchRequest(exclude_ingredients=["花生"]))
    item = next(item for item in result["items"] if item["product_code"] == "FP0017")
    assert item["match_status"] == "NOT_MATCH"
    assert item["reason_source"] == "exclude"
    assert item["reason"] == "含有用户排除成分：花生"


def test_dynamic_sugar_limit_marks_high_sugar_product_not_match():
    request = FilterSearchRequest.model_validate({
        "nutrition_targets": [{
            "nutrient_code": "NUT_SUGAR", "nutrient_name": "糖", "operator": "LTE",
            "value": "8", "unit": "g",
        }]
    })
    result = filter_service().search(request)
    item = next(item for item in result["items"] if item["product_code"] == "FP0017")
    assert item["match_status"] == "NOT_MATCH"
    assert item["reason_source"] == "nutrition"
    assert item["reason"] == "糖12g超过限制8g"
    assert result["conditions"].nutrition_targets[0].value == Decimal("8")


def test_empty_nutrition_conditions_do_not_apply_fixed_thresholds():
    analyzed = ControlledFilterAnalyzer().analyze("低糖商品")
    assert analyzed.nutrition_targets == []

def test_not_want_bread_is_normalized_to_excluded_category():
    result = ControlledFilterAnalyzer().analyze("我不想吃面包")
    assert result.exclude_categories == ["CAT006"]
    assert result.category_code is None


def test_bread_category_is_removed_from_search_results():
    result = filter_service().search(FilterSearchRequest(exclude_categories=["CAT006"]))
    assert "FP0008" not in {item["product_code"] for item in result["items"]}


def test_frontend_category_name_is_normalized_before_search():
    request = FilterSearchRequest(exclude_categories=["面包烘焙"])
    assert request.exclude_categories == ["CAT006"]
    result = filter_service().search(request)
    assert "FP0008" not in {item["product_code"] for item in result["items"]}

def test_ingredient_alias_keeps_ingredient_exclusion_precedence():
    result = ControlledFilterAnalyzer().analyze("不含牛奶")
    assert result.exclude_ingredients == ["牛奶"]
    assert result.exclude_categories == []
