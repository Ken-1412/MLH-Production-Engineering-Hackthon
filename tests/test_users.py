import io

from app.models.user import User


def test_list_users_empty(client):
    r = client.get("/users")
    assert r.status_code == 200
    data = r.get_json()
    assert "data" in data
    assert "count" in data
    assert data["count"] == 0
    assert data["data"] == []


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


def test_create_user_missing_email(client):
    r = client.post("/users", json={"username": "nomail"})
    assert r.status_code == 400
    assert "error" in r.get_json()


def test_create_user_missing_username(client):
    r = client.post("/users", json={"email": "nousername@test.com"})
    assert r.status_code == 400
    assert "error" in r.get_json()


def test_create_user_invalid_json(client):
    r = client.post(
        "/users",
        data="not json",
        content_type="application/json",
    )
    assert r.status_code == 400


def test_get_user_non_integer_id(client):
    r = client.get("/users/abc")
    assert r.status_code == 404
    assert "error" in r.get_json()


def test_update_user_not_found(client):
    r = client.put("/users/999999", json={"username": "x"})
    assert r.status_code == 404


def test_update_user_invalid_json(client):
    created = client.post("/users", json={"username": "test1", "email": "test1@example.com"}).get_json()
    r = client.put(
        f"/users/{created['id']}",
        data="not json",
        content_type="application/json",
    )
    assert r.status_code == 400


def test_update_user_invalid_field_type(client):
    created = client.post("/users", json={"username": "test1", "email": "test1@example.com"}).get_json()
    r = client.put(f"/users/{created['id']}", json={"username": 12345})
    assert r.status_code == 400


def test_list_users_after_create(client):
    client.post("/users", json={"username": "list1", "email": "list1@test.com"})
    r = client.get("/users")
    data = r.get_json()
    assert data["count"] >= 1


def test_bulk_load_no_file(client):
    r = client.post("/users/bulk", content_type="multipart/form-data")
    assert r.status_code == 400


def test_update_user_duplicate(client):
    client.post("/users", json={"username": "dup1", "email": "dup1@test.com"})
    created2 = client.post("/users", json={"username": "dup2", "email": "dup2@test.com"}).get_json()
    r = client.put(f"/users/{created2['id']}", json={"username": "dup1"})
    assert r.status_code == 409
