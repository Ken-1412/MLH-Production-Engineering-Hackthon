"""Tests for the /urls CRUD endpoints."""

import json


# ── BRONZE: basic route existence ─────────────────────────────────────


def test_list_returns_200(client):
    r = client.get("/urls")
    assert r.status_code == 200


def test_list_returns_data_and_count_keys(client):
    data = client.get("/urls").get_json()
    assert "data" in data and "count" in data


def test_list_count_matches_data_length(client):
    data = client.get("/urls").get_json()
    assert data["count"] == len(data["data"])


def test_create_valid_returns_201(client):
    r = client.post(
        "/urls",
        json={
            "user_id": 1,
            "short_code": "abc123",
            "original_url": "https://example.com",
            "title": "Example",
        },
    )
    assert r.status_code == 201


def test_create_valid_returns_data_key(client):
    r = client.post(
        "/urls",
        json={
            "user_id": 1,
            "short_code": "def456",
            "original_url": "https://example.com",
            "title": "Example",
        },
    )
    assert "data" in r.get_json()


# ── SILVER: full integration (request → DB → response) ────────────────


def test_create_then_get_by_id(client):
    created = client.post(
        "/urls",
        json={
            "user_id": 1,
            "short_code": "ghi789",
            "original_url": "https://example.com",
            "title": "Get Test",
        },
    ).get_json()
    record_id = created["data"]["id"]
    r = client.get(f"/urls/{record_id}")
    assert r.status_code == 200
    assert r.get_json()["data"]["id"] == record_id


def test_create_duplicate_returns_409(client, sample):
    # sample already exists — try to create the same short_code
    r = client.post(
        "/urls",
        json={
            "user_id": 2,
            "short_code": sample.short_code,
            "original_url": "https://other.com",
            "title": "Duplicate",
        },
    )
    assert r.status_code == 409
    assert "error" in r.get_json()


def test_create_missing_required_field_returns_400(client):
    r = client.post("/urls", json={})
    assert r.status_code == 400
    data = r.get_json()
    assert "error" in data


def test_create_invalid_type_returns_400(client):
    r = client.post(
        "/urls",
        json={
            "user_id": "not-a-number",
            "short_code": "xyz999",
            "original_url": "https://example.com",
            "title": "Bad Type",
        },
    )
    assert r.status_code == 400


def test_create_no_body_returns_400(client):
    r = client.post(
        "/urls",
        data="not json",
        content_type="application/json",
    )
    assert r.status_code == 400


def test_create_empty_json_object_returns_400(client):
    r = client.post("/urls", json={})
    assert r.status_code == 400


def test_get_nonexistent_id_returns_404(client):
    r = client.get("/urls/999999")
    assert r.status_code == 404
    assert "error" in r.get_json()


def test_get_string_id_returns_404(client):
    r = client.get("/urls/not-an-id")
    assert r.status_code in (400, 404)
    assert "error" in r.get_json()


def test_update_existing_returns_200(client, sample):
    r = client.put(
        f"/urls/{sample.id}",
        json={"title": "Updated Name"},
    )
    assert r.status_code == 200


def test_update_nonexistent_returns_404(client):
    r = client.put("/urls/999999", json={"title": "x"})
    assert r.status_code == 404


def test_update_invalid_field_returns_400(client, sample):
    r = client.put(
        f"/urls/{sample.id}",
        json={"is_active": "banana"},
    )
    assert r.status_code == 400


def test_delete_existing_returns_204(client, sample):
    r = client.delete(f"/urls/{sample.id}")
    assert r.status_code == 204


def test_delete_nonexistent_returns_404(client):
    r = client.delete("/urls/999999")
    assert r.status_code == 404


def test_delete_same_record_twice_second_is_404(client, sample):
    client.delete(f"/urls/{sample.id}")
    r = client.delete(f"/urls/{sample.id}")
    assert r.status_code == 404


# ── GOLD: edge cases and consistency ──────────────────────────────────


def test_error_responses_never_return_html(client):
    for url in ["/urls/abc", "/urls/999999"]:
        r = client.get(url)
        assert "text/html" not in r.content_type


def test_list_after_create_count_increases(client):
    before = client.get("/urls").get_json()["count"]
    client.post(
        "/urls",
        json={
            "user_id": 1,
            "short_code": "cnt001",
            "original_url": "https://example.com",
            "title": "Count Test",
        },
    )
    after = client.get("/urls").get_json()["count"]
    assert after == before + 1


def test_get_after_delete_returns_404(client, sample):
    client.delete(f"/urls/{sample.id}")
    r = client.get(f"/urls/{sample.id}")
    assert r.status_code == 404


def test_extra_fields_in_body_do_not_crash(client):
    r = client.post(
        "/urls",
        json={
            "user_id": 1,
            "short_code": "ext001",
            "original_url": "https://example.com",
            "title": "Extra Fields",
            "surprise": "field",
            "another": 999,
        },
    )
    # Either 201 (extra fields ignored) or 400 (rejected) — never 500
    assert r.status_code in (201, 400)


def test_all_error_responses_have_error_key(client):
    cases = [
        client.get("/urls/999999"),
        client.post("/urls", json={}),
        client.delete("/urls/999999"),
    ]
    for r in cases:
        assert "error" in r.get_json(), f"Missing 'error' key for {r.status_code}"


def test_search_filter_by_title(client):
    client.post(
        "/urls",
        json={
            "user_id": 1,
            "short_code": "srch01",
            "original_url": "https://example.com",
            "title": "UniqueSearchTitle",
        },
    )
    r = client.get("/urls?search=UniqueSearchTitle")
    data = r.get_json()
    assert r.status_code == 200
    assert data["count"] >= 1
    assert any("UniqueSearchTitle" in item["title"] for item in data["data"])


def test_search_no_results(client):
    r = client.get("/urls?search=zzzzzzz_nonexistent_zzzzzzz")
    data = r.get_json()
    assert r.status_code == 200
    assert data["count"] == 0
    assert data["data"] == []


def test_create_returns_all_fields(client):
    r = client.post(
        "/urls",
        json={
            "user_id": 5,
            "short_code": "fld001",
            "original_url": "https://example.com/all-fields",
            "title": "All Fields Test",
            "is_active": False,
        },
    )
    data = r.get_json()["data"]
    assert "id" in data
    assert data["short_code"] == "fld001"
    assert data["original_url"] == "https://example.com/all-fields"
    assert data["title"] == "All Fields Test"
    assert data["is_active"] is False
    assert data["user_id"] == 5
    assert "created_at" in data
    assert "updated_at" in data


def test_update_preserves_unchanged_fields(client, sample):
    original = client.get(f"/urls/{sample.id}").get_json()["data"]
    client.put(f"/urls/{sample.id}", json={"title": "Changed"})
    updated = client.get(f"/urls/{sample.id}").get_json()["data"]
    assert updated["title"] == "Changed"
    assert updated["short_code"] == original["short_code"]
    assert updated["original_url"] == original["original_url"]


def test_method_not_allowed_returns_json(client):
    r = client.patch("/urls")
    assert r.status_code == 405
    data = r.get_json()
    assert "error" in data


def test_create_with_missing_short_code_returns_field_error(client):
    r = client.post(
        "/urls",
        json={
            "user_id": 1,
            "original_url": "https://example.com",
            "title": "No Code",
        },
    )
    assert r.status_code == 400
    data = r.get_json()
    assert "fields" in data
    assert "short_code" in data["fields"]
