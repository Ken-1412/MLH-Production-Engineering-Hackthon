import io

from app.models.user import User


def test_list_users_empty(client):
    r = client.get("/users")
    assert r.status_code == 200
    assert r.get_json() == []


def test_create_user(client):
    r = client.post("/users", json={"username": "test1", "email": "test1@example.com"})
    assert r.status_code == 201
    data = r.get_json()
    assert data["username"] == "test1"
    assert "id" in data


def test_create_user_duplicate(client):
    client.post("/users", json={"username": "test1", "email": "test1@example.com"})
    r = client.post("/users", json={"username": "test1", "email": "test1@example.com"})
    assert r.status_code == 409


def test_get_user(client):
    created = client.post("/users", json={"username": "test1", "email": "test1@example.com"}).get_json()
    r = client.get(f"/users/{created['id']}")
    assert r.status_code == 200
    assert r.get_json()["username"] == "test1"


def test_get_user_not_found(client):
    r = client.get("/users/999")
    assert r.status_code == 404


def test_update_user(client):
    created = client.post("/users", json={"username": "test1", "email": "test1@example.com"}).get_json()
    r = client.put(f"/users/{created['id']}", json={"username": "updated_user"})
    assert r.status_code == 200
    assert r.get_json()["username"] == "updated_user"


def test_bulk_load_users(client):
    csv_content = "username,email\nbulk1,bulk1@example.com\nbulk2,bulk2@example.com"
    r = client.post(
        "/users/bulk",
        data={"file": (io.BytesIO(csv_content.encode("utf-8")), "users.csv")},
        content_type="multipart/form-data"
    )
    assert r.status_code == 201
    assert r.get_json()["count"] == 2
