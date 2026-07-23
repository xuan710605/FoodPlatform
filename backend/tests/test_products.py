def test_product_list_pagination(client):
    response = client.get("/api/v1/products?page=2&page_size=10")
    assert response.status_code == 200
    assert response.json()["data"]["page"] == 2
    assert response.json()["data"]["page_size"] == 10


def test_page_size_limit(client):
    response = client.get("/api/v1/products?page_size=101")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_illegal_sort_by(client):
    response = client.get("/api/v1/products?sort_by=drop_table")
    assert response.status_code == 422


def test_product_not_found(client):
    response = client.get("/api/v1/products/FP9999")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "PRODUCT_NOT_FOUND"


def test_product_detail_structure_and_decimal(client):
    response = client.get("/api/v1/products/FP0001")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["raw_ingredient_text"] == "燕麦"
    assert data["contains"][0]["relation_type"] == "CONTAINS"
    assert data["unknown"][0]["relation_type"] == "UNKNOWN"
    assert data["sales_quantity"] == 12
    assert data["average_rating"] == "4.50"
    assert data["review_count"] == 2
    assert data["match_status"] == "FULL_MATCH"
    assert data["evidence_text"]
    assert data["nutrition"][0]["unit"] == "g"
    assert data["nutrition"][0]["basis"] == "PER_100G"
    assert data["specs"][0]["sale_price"] == "32.90"
