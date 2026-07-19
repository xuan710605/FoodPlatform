from tests.conftest import FakeDriver, FakeEngine


def test_liveness(client):
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json()["data"] == {"service": "ok"}


def test_health_success(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["data"] == {"service": "ok", "mysql": "ok", "neo4j": "ok"}


def test_ready_mysql_failure_is_safe(client):
    client.app.state.mysql_engine = FakeEngine(failing=True)
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 503
    assert response.json()["data"]["mysql"] == "error"
    assert "must_not_leak" not in response.text


def test_ready_neo4j_failure_is_safe(client):
    client.app.state.neo4j_driver = FakeDriver(failing=True)
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 503
    assert response.json()["data"]["neo4j"] == "error"
    assert "must_not_leak" not in response.text
