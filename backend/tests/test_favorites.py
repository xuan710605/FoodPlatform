AUTH={"Authorization":"Bearer good-token"}

def test_favorite_requires_login(client):
    assert client.get("/api/v1/favorites").status_code==401

def test_add_list_and_delete_favorite(client):
    created=client.post("/api/v1/favorites",json={"product_code":"FP0001"},headers=AUTH)
    assert created.status_code==201
    assert created.json()["data"]["product_code"]=="FP0001"
    listed=client.get("/api/v1/favorites",headers=AUTH)
    assert listed.status_code==200
    assert [item["product_code"] for item in listed.json()["data"]]==["FP0001"]
    assert client.delete("/api/v1/favorites/FP0001",headers=AUTH).status_code==200

def test_favorites_are_isolated_by_user_id():
    from tests.conftest import FakeFavoriteService
    service=FakeFavoriteService()
    service.add(21,"FP0001")
    assert len(service.list(21))==1
    assert service.list(22)==[]

def test_confirm_receipt(client):
    response=client.post("/api/v1/orders/31/confirm-receipt",headers=AUTH)
    assert response.status_code==200
    assert response.json()["data"]["status"]=="COMPLETED"
