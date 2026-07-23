import os
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("MYSQL_PASSWORD", "unit_test_only")
os.environ.setdefault("NEO4J_PASSWORD", "unit_test_only")
os.environ.setdefault("JWT_SECRET", "unit-test-jwt-secret-at-least-32-characters")

from app.main import app  # noqa: E402
from app.services.filter_rules import ControlledFilterAnalyzer  # noqa: E402


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

    def login(self, _identity, password):
        if password == "wrong-password":
            from app.core.exceptions import AppError
            raise AppError("INVALID_CREDENTIALS", "Invalid username/email or password", 401)
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

class FakeFilterService:
    def analyze(self, text):
        return ControlledFilterAnalyzer().analyze(text).model_dump()

    def search(self, payload):
        return {
            "total": 1, "page": payload.page, "page_size": payload.page_size,
            "conditions": {
                "exclude_ingredients": payload.exclude_ingredients,
                "nutrition_targets": payload.nutrition_targets,
                "max_price": payload.max_price,
                "category_code": payload.category_code,
            },
            "items": [{
                "product_code": "FP0001", "name": "原味燕麦片", "brand": "谷物日记",
                "category": "早餐麦片", "main_image_url": None, "sale_price": Decimal("32.90"),
                "match_status": "MATCH", "reasons": ["满足当前条件"],
                "contains_hits": [], "may_contain_hits": [],
            }],
        }


class FakeCartService:
    item = {"id": 7, "product_code": "FP0001", "product_name": "原味燕麦片", "spec_code": "SPEC001", "spec_name": "500g", "image_url": None, "quantity": 1, "unit_price": Decimal("32.90"), "subtotal": Decimal("32.90"), "stock_quantity": 88, "sellable": True, "selected": True}
    def get(self, _user_id): return {"cart_code":"CARTTEST","items":[self.item],"item_count":1,"total_quantity":1,"total_amount":Decimal("32.90")}
    def add(self, _user_id, payload):
        from app.core.exceptions import AppError
        if payload["quantity"] > 88: raise AppError("INSUFFICIENT_STOCK","Insufficient product stock",409)
        return self.item | {"quantity":payload["quantity"],"subtotal":Decimal("32.90")*payload["quantity"]}
    def update(self, _user_id, item_id, quantity): return self.item | {"id":item_id,"quantity":quantity,"subtotal":Decimal("32.90")*quantity}
    def delete(self, _user_id, _item_id): return None

class FakeAddressService:
    def __init__(self):
        self.last_user_id = None
        self.item = {
            "address_code": "ADDRTEST01", "receiver_name": "测试用户",
            "receiver_phone": "13800000000", "province": "上海市", "city": "上海市",
            "district": "徐汇区", "detail_address": "虹桥路718号", "postal_code": "200030",
            "is_default": True, "created_at": datetime(2026,7,23,tzinfo=timezone.utc),
            "updated_at": datetime(2026,7,23,tzinfo=timezone.utc),
        }
    def list(self,user_id): self.last_user_id=user_id; return [self.item]
    def create(self,user_id,payload): self.last_user_id=user_id; return self.item | payload
    def update(self,user_id,address_code,payload): self.last_user_id=user_id; return self.item | payload | {"address_code":address_code}
    def delete(self,user_id,_address_code): self.last_user_id=user_id
    def set_default(self,user_id,address_code): self.last_user_id=user_id; return self.item | {"address_code":address_code,"is_default":True}

class FakeOrderService:
    item={"id":31,"order_no":"ORDTEST31","status":"PENDING_PAYMENT","payment_status":"UNPAID","goods_amount":Decimal("32.90"),"shipping_amount":Decimal("6"),"payable_amount":Decimal("38.90"),"paid_amount":Decimal("0"),"placed_at":datetime(2026,7,23,tzinfo=timezone.utc),"paid_at":None,"items":[{"id":51,"product_code":"FP0001","product_name":"原味燕麦片","spec_code":"SPEC001","spec_name":"500g","image_url":None,"unit_price":Decimal("32.90"),"quantity":1,"subtotal":Decimal("32.90"),"ingredient_version":1}]}
    def create(self,_user_id,_payload): return self.item
    def list(self,_user_id,page,page_size): return {"total":1,"page":page,"page_size":page_size,"items":[self.item]}
    def get(self,_user_id,_order_id): return self.item
    def pay(self,_user_id,_order_id,_channel): return self.item|{"status":"PAID","payment_status":"PAID","paid_amount":Decimal("38.90"),"paid_at":datetime(2026,7,23,tzinfo=timezone.utc)}
    def cancel(self,_user_id,_order_id): return self.item|{"status":"CANCELLED"}

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
        app.state.filter_service = FakeFilterService()
        app.state.cart_service = FakeCartService()
        app.state.address_service = FakeAddressService()
        app.state.order_service = FakeOrderService()
        yield test_client
