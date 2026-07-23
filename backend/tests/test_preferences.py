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


def test_get_food_preferences_for_current_user(client):
    response = client.get("/api/v1/users/preferences", headers=AUTH)
    assert response.status_code == 200
    assert response.json()["data"] == {"exclude_ingredients": [], "preferred_ingredients": []}


def test_replace_food_preferences_for_current_user(client):
    response = client.put(
        "/api/v1/users/preferences",
        headers=AUTH,
        json={"exclude_ingredients": ["花生", "花生粉"], "preferred_ingredients": ["燕麦", "高蛋白"]},
    )
    assert response.status_code == 200
    assert response.json()["data"]["exclude_ingredients"] == ["花生", "花生粉"]
    loaded = client.get("/api/v1/users/preferences", headers=AUTH)
    assert loaded.json()["data"]["preferred_ingredients"] == ["燕麦", "高蛋白"]


def test_food_preferences_require_authentication(client):
    assert client.get("/api/v1/users/preferences").status_code == 401
    assert client.put("/api/v1/users/preferences", json={"exclude_ingredients": [], "preferred_ingredients": []}).status_code == 401