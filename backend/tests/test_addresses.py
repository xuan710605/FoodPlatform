from datetime import datetime, timezone

AUTH = {"Authorization": "Bearer good-token"}


def payload(name: str = "测试用户", default: bool = False) -> dict:
    return {
        "receiver_name": name,
        "receiver_phone": "13800000000",
        "province": "上海市",
        "city": "上海市",
        "district": "徐汇区",
        "detail_address": "虹桥路718号",
        "postal_code": "200030",
        "is_default": default,
    }


def test_create_address(client):
    response = client.post("/api/v1/addresses", json=payload(default=True), headers=AUTH)
    assert response.status_code == 201
    assert response.json()["data"]["address_code"] == "ADDRTEST01"
    assert response.json()["data"]["is_default"] is True


def test_list_only_current_users_addresses(client):
    response = client.get("/api/v1/addresses", headers=AUTH)
    assert response.status_code == 200
    assert response.json()["data"][0]["receiver_name"] == "测试用户"
    assert client.app.state.address_service.last_user_id == 21


def test_update_address(client):
    response = client.put("/api/v1/addresses/ADDRTEST01", json=payload("新收货人"), headers=AUTH)
    assert response.status_code == 200
    assert response.json()["data"]["receiver_name"] == "新收货人"


def test_delete_address(client):
    response = client.delete("/api/v1/addresses/ADDRTEST01", headers=AUTH)
    assert response.status_code == 200
    assert response.json()["data"]["address_code"] == "ADDRTEST01"


def test_switch_default_address(client):
    response = client.put("/api/v1/addresses/ADDRTEST02/default", headers=AUTH)
    assert response.status_code == 200
    assert response.json()["data"]["address_code"] == "ADDRTEST02"
    assert response.json()["data"]["is_default"] is True


class AddressRepositoryStub:
    def __init__(self):
        self.address = {
            "address_code": "ADDR-A",
            "receiver_name": "用户A",
            "receiver_phone": "13800000000",
            "province": "上海市",
            "city": "上海市",
            "district": "徐汇区",
            "detail_address": "测试路1号",
            "postal_code": None,
        }

    def get_for_user(self, user_id, address_code):
        return self.address if user_id == 21 and address_code == "ADDR-A" else None


class OrderRepositoryStub:
    def __init__(self):
        self.receiver = None

    def create_order(self, _user_id, _items, receiver, _remark):
        self.receiver = dict(receiver)
        return {"id": 1, "status": "PENDING_PAYMENT"}


def test_order_rejects_another_users_address():
    from app.core.exceptions import AppError
    from app.services.order_service import OrderService

    service = OrderService(OrderRepositoryStub(), AddressRepositoryStub())
    try:
        service.create(22, {"cart_item_ids": [1], "address_code": "ADDR-A", "buyer_remark": None})
    except AppError as exc:
        assert exc.code == "ADDRESS_NOT_FOUND"
    else:
        raise AssertionError("foreign address must be rejected")


def test_order_saves_address_snapshot():
    from app.services.order_service import OrderService

    order_repository = OrderRepositoryStub()
    service = OrderService(order_repository, AddressRepositoryStub())
    service.create(21, {"cart_item_ids": [1], "address_code": "ADDR-A", "buyer_remark": None})
    assert order_repository.receiver == {
        "address_code": "ADDR-A",
        "name": "用户A",
        "phone": "13800000000",
        "province": "上海市",
        "city": "上海市",
        "district": "徐汇区",
        "detail_address": "测试路1号",
        "postal_code": None,
        "address": "上海市上海市徐汇区测试路1号",
    }
    # Changing the source object cannot mutate the dict passed to order persistence.
    service.address_repository.address["detail_address"] = "修改后的地址"
    assert order_repository.receiver["detail_address"] == "测试路1号"
