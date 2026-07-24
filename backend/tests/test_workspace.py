PRODUCT_PAYLOAD = {"name":"新商品","brand_code":"BR001","category_code":"CAT001","raw_ingredient_text":"燕麦","spec_name":"500g","unit_name":"袋","price":"29.90","stock_quantity":20}


def auth(token): return {"Authorization": f"Bearer {token}"}


def test_merchant_dashboard_requires_merchant_role(client):
    assert client.get("/api/v1/merchant/dashboard").status_code == 401
    assert client.get("/api/v1/merchant/dashboard",headers=auth("good-token")).status_code == 403
    response=client.get("/api/v1/merchant/dashboard",headers=auth("merchant-token"))
    assert response.status_code == 200
    assert response.json()["data"]["merchant_code"] == "MCH0001"


def test_merchant_product_crud_contract(client):
    headers=auth("merchant-token")
    assert client.get("/api/v1/merchant/products",headers=headers).status_code == 200
    assert client.post("/api/v1/merchant/products",headers=headers,json=PRODUCT_PAYLOAD).status_code == 201
    assert client.put("/api/v1/merchant/products/FP0099",headers=headers,json=PRODUCT_PAYLOAD).status_code == 200
    assert client.put("/api/v1/merchant/products/FP0099/sale-status",headers=headers,json={"sale_status":"ON_SALE"}).status_code == 200


def test_merchant_order_transition_contract(client):
    headers=auth("merchant-token")
    orders=client.get("/api/v1/merchant/orders",headers=headers)
    assert orders.status_code == 200
    assert orders.json()["data"][0]["status"] == "PAID"
    assert orders.json()["data"][1]["status"] == "REFUND_REQUESTED"
    assert client.put("/api/v1/merchant/orders/1/status",headers=headers,json={"status":"SHIPPING"}).status_code == 200


def test_merchant_orders_return_empty_list(client, monkeypatch):
    monkeypatch.setattr(client.app.state.workspace_service, "merchant_orders", lambda _user_id: [])
    response = client.get("/api/v1/merchant/orders", headers=auth("merchant-token"))
    assert response.status_code == 200
    assert response.json()["data"] == []

def test_admin_endpoints_require_admin_role(client):
    assert client.get("/api/v1/admin/dashboard",headers=auth("merchant-token")).status_code == 403
    dashboard=client.get("/api/v1/admin/dashboard",headers=auth("admin-token"))
    assert dashboard.status_code == 200
    assert dashboard.json()["data"]["product_count"] == 20
    users=client.get("/api/v1/admin/users",headers=auth("admin-token"))
    assert users.status_code == 200
    searched=client.get("/api/v1/admin/users?keyword=merchant",headers=auth("admin-token"))
    assert searched.status_code == 200
    assert [user["username"] for user in searched.json()["data"]] == ["merchant_zhiwei"]
    disabled=client.put("/api/v1/admin/users/8/status",headers=auth("admin-token"),json={"status":"DISABLED"})
    assert disabled.status_code == 200
    assert disabled.json()["data"] == {"id":8,"status":"DISABLED"}
    enabled=client.put("/api/v1/admin/users/8/status",headers=auth("admin-token"),json={"status":"ACTIVE"})
    assert enabled.status_code == 200
    assert enabled.json()["data"] == {"id":8,"status":"ACTIVE"}


def test_admin_pending_products_and_approval(client):
    headers=auth("admin-token")
    products=client.get("/api/v1/admin/products",headers=headers)
    assert products.status_code == 200
    assert products.json()["data"][0]["review_status"] == "PENDING"
    approved=client.put("/api/v1/admin/products/FP0099/approve",headers=headers,json={"opinion":"资料完整"})
    assert approved.status_code == 200
    assert approved.json()["data"]["review_status"] == "APPROVED"