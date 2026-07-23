import os
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("MYSQL_PASSWORD", "unit_test_only")
os.environ.setdefault("NEO4J_PASSWORD", "unit_test_only")
os.environ.setdefault("JWT_SECRET", "unit-test-jwt-secret-at-least-32-characters")

from app.main import app  # noqa: E402


class Result:
    def consume(self):
        return None


class FakeConnection:
    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None

    def execute(self, _):
        return Result()


class FakeEngine:
    def __init__(self, failing: bool = False):
        self.failing = failing

    def connect(self):
        if self.failing:
            raise RuntimeError("mysql password=must_not_leak")
        return FakeConnection()


class FakeNeo4jSession(FakeConnection):
    def run(self, *_args, **_kwargs):
        return Result()


class FakeDriver:
    def __init__(self, failing: bool = False):
        self.failing = failing

    def session(self, **_kwargs):
        if self.failing:
            raise RuntimeError("neo4j password=must_not_leak")
        return FakeNeo4jSession()


PRODUCT = {
    "id": 1, "product_code": "FP0001", "name": "原味燕麦片", "subtitle": "配料简单",
    "brand": "谷物日记", "brand_code": "BR001", "category": "早餐麦片", "category_code": "CAT001",
    "merchant": "知味食品旗舰店", "merchant_id": 1, "main_image_url": "https://example.test/oat.jpg",
    "sale_price": Decimal("32.90"), "market_price": Decimal("39.90"), "stock_quantity": 88, "sellable": True,
    "audit_status": "APPROVED", "sale_status": "ON_SALE", "ingredient_version": 1,
    "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc), "updated_at": datetime(2026, 1, 2, tzinfo=timezone.utc),
}

DETAIL = {
    "id": 1, "product_code": "FP0001", "name": "原味燕麦片", "subtitle": "配料简单", "description": "早餐",
    "brand": "谷物日记", "brand_code": "BR001", "category": "早餐麦片", "category_code": "CAT001",
    "merchant": {"merchant_code": "MER001", "name": "知味食品旗舰店"},
    "raw_ingredient_text": "燕麦", "allergen_notice": None, "ingredient_version": 1, "graph_sync_status": "SYNCED",
    "specs": [{"spec_code": "SPEC001", "spec_name": "500g", "unit_name": "袋", "net_content_value": Decimal("500"), "net_content_unit": "g", "is_default": True, "sale_price": Decimal("32.90"), "market_price": Decimal("39.90"), "currency": "CNY", "stock_quantity": 88, "sellable": True}],
    "images": [{"image_type": "MAIN", "image_url": "https://example.test/oat.jpg", "alt_text": "燕麦片", "sort_order": 0}],
    "nutrition": [{"nutrient_code": "NUT001", "nutrient_name": "蛋白质", "value": Decimal("12.3"), "unit": "g", "basis": "PER_100G", "basis_quantity": Decimal("100"), "source_code": "SRC001"}],
    "contains": [{"entity_code": "ING001", "name": "燕麦", "entity_type": "INGREDIENT", "relation_type": "CONTAINS", "confidence": Decimal("1"), "source_code": "SRC001", "audit_status": "APPROVED"}],
    "may_contain": [], "audit_status": "APPROVED", "sale_status": "ON_SALE",
    "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc), "updated_at": datetime(2026, 1, 2, tzinfo=timezone.utc),
}

GRAPH = {
    "nodes": [
        {"data": {"id": "FoodProduct:FP0017", "type": "FoodProduct", "business_code": "FP0017", "label": "花生巧克力"}},
        {"data": {"id": "Ingredient:ING004", "type": "Ingredient", "business_code": "ING004", "label": "花生酱"}},
        {"data": {"id": "Ingredient:ING002", "type": "Ingredient", "business_code": "ING002", "label": "花生"}},
    ],
    "edges": [
        {"data": {"id": "contains", "source": "FoodProduct:FP0017", "target": "Ingredient:ING004", "type": "FOOD_PRODUCT_CONTAINS_INGREDIENT", "confidence": 1.0, "source_code": "SRC001", "audit_status": "APPROVED"}},
        {"data": {"id": "may", "source": "FoodProduct:FP0017", "target": "Ingredient:ING002", "type": "FOOD_PRODUCT_MAY_CONTAIN", "confidence": 0.9, "source_code": "SRC001", "audit_status": "APPROVED"}},
    ],
    "summary": {"contains_count": 1, "may_contain_count": 1, "risk_count": 0, "information_status": "SUFFICIENT"},
}


class FakeProductService:
    def list_products(self, filters):
        return {"total": 1, "page": filters["page"], "page_size": filters["page_size"], "items": [PRODUCT]}

    def get_detail(self, code):
        from app.core.exceptions import AppError
        if code == "FP9999":
            raise AppError("PRODUCT_NOT_FOUND", "Product not found", 404)
        return DETAIL



AUTH_USER = {
    "id": 21, "user_code": "USRTEST21", "username": "test_consumer",
    "email": "consumer@example.test", "user_type": "CONSUMER", "status": "ACTIVE",
    "roles": ["CONSUMER"], "created_at": datetime(2026, 7, 23, tzinfo=timezone.utc),
}


class FakeAuthService:
    def register(self, username, email, _password, _nickname):
        return AUTH_USER | {"username": username, "email": email}

    def login(self, _identity, _password):
        return {"access_token": "good-token", "token_type": "bearer", "expires_in": 3600, "user": AUTH_USER}

    def authenticate_token(self, token):
        from app.core.exceptions import AppError
        if token != "good-token":
            raise AppError("INVALID_TOKEN", "Access token is invalid or expired", 401)
        return AUTH_USER


class FakePreferenceService:
    item = {
        "id": 1, "preference_code": "PREF001", "kind": "ALLERGEN", "code": "ING002",
        "name": "花生", "preference_type": "EXCLUDE", "strength": 100, "is_enabled": True,
        "created_at": datetime(2026, 7, 23, tzinfo=timezone.utc),
        "updated_at": datetime(2026, 7, 23, tzinfo=timezone.utc),
    }

    def list_preferences(self, _user_id):
        return [self.item]

    def create_preference(self, _user_id, payload):
        return self.item | {"kind": payload["kind"], "code": payload["code"], "name": payload["name"]}

    def delete_preference(self, _user_id, _preference_id):
        return None


class FakeCatalogService:
    def categories(self):
        return [{"category_code": "CAT001", "name": "早餐麦片", "parent_code": None, "level": 1, "sort_order": 1}]

    def brands(self):
        return [{"brand_code": "BR001", "name": "谷物日记", "logo_url": None, "description": None}]

class FakeGraphService:
    def get_product_graph(self, _code):
        return GRAPH


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        app.state.mysql_engine = FakeEngine()
        app.state.neo4j_driver = FakeDriver()
        app.state.product_service = FakeProductService()
        app.state.graph_service = FakeGraphService()
        app.state.auth_service = FakeAuthService()
        app.state.preference_service = FakePreferenceService()
        app.state.catalog_service = FakeCatalogService()
        yield test_client
