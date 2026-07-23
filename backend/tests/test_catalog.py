def test_categories(client):
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    assert response.json()["data"][0]["category_code"] == "CAT001"


def test_brands(client):
    response = client.get("/api/v1/brands")
    assert response.status_code == 200
    assert response.json()["data"][0]["brand_code"] == "BR001"
