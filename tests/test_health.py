"""Tests for the /health endpoint."""


def test_health_status_200(client):
    r = client.get("/health")
    assert r.status_code == 200


def test_health_content_type_json(client):
    r = client.get("/health")
    assert "application/json" in r.content_type


def test_health_body_has_status_ok(client):
    data = client.get("/health").get_json()
    assert data["status"] == "ok"


def test_health_body_has_db_field(client):
    data = client.get("/health").get_json()
    assert "db" in data


def test_health_always_200_structure(client):
    # Ensure shape is always correct regardless of DB state
    data = client.get("/health").get_json()
    assert set(data.keys()) >= {"status", "db"}
