AUTH = {"Authorization": "Bearer good-token"}


def test_create_preference(client):
    response = client.post(
        "/api/v1/preferences",
        headers=AUTH,
        json={"kind": "ALLERGEN", "code": "ING002", "name": "花生", "strength": 100},
    )
    assert response.status_code == 201
    assert response.json()["data"]["preference_type"] == "EXCLUDE"


def test_list_preferences(client):
    response = client.get("/api/v1/preferences", headers=AUTH)
    assert response.status_code == 200
    assert response.json()["data"][0]["kind"] == "ALLERGEN"


def test_delete_preference(client):
    response = client.delete("/api/v1/preferences/1", headers=AUTH)
    assert response.status_code == 200
    assert response.json()["data"] == {"id": 1}
