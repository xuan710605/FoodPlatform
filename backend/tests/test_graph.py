def test_graph_response_uses_business_ids(client):
    response = client.get("/api/v1/products/FP0017/graph")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["nodes"] and data["edges"]
    for node in data["nodes"]:
        assert set(node["data"]) <= {"id", "type", "business_code", "label", "risk_level"}
        assert node["data"]["id"].startswith(node["data"]["type"] + ":")


def test_contains_and_may_contain_are_distinct(client):
    edges = client.get("/api/v1/products/FP0017/graph").json()["data"]["edges"]
    edge_types = {edge["data"]["type"] for edge in edges}
    assert "FOOD_PRODUCT_CONTAINS_INGREDIENT" in edge_types
    assert "FOOD_PRODUCT_MAY_CONTAIN" in edge_types
    assert "CONTAINS" not in edge_types
