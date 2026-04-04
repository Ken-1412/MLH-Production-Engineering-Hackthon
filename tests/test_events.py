from app.models.event import Event


def test_list_events_empty(client):
    r = client.get("/events")
    assert r.status_code == 200
    data = r.get_json()
    assert "data" in data
    assert "count" in data
    assert data["count"] == 0


def test_list_events_with_data(client):
    Event.create(url_id=1, user_id=1, event_type="click")
    r = client.get("/events")
    assert r.status_code == 200
    data = r.get_json()
    assert data["count"] == 1
    assert data["data"][0]["event_type"] == "click"


def test_event_details_json_parsed(client):
    Event.create(url_id=1, user_id=1, event_type="click", details='{"browser": "chrome"}')
    r = client.get("/events")
    data = r.get_json()
    assert data["data"][0]["details"] == {"browser": "chrome"}


def test_event_details_empty(client):
    Event.create(url_id=1, user_id=1, event_type="view")
    r = client.get("/events")
    data = r.get_json()
    assert data["data"][0]["details"] == {}


def test_event_safe_get(app):
    event = Event.create(url_id=1, user_id=1, event_type="click")
    assert Event.safe_get(event.id) is not None
    assert Event.safe_get(999999) is None
    assert Event.safe_get("abc") is None


def test_event_get_details_method(app):
    event = Event.create(url_id=1, user_id=1, event_type="click", details='{"key": "val"}')
    assert event.get_details() == {"key": "val"}


def test_event_get_details_invalid_json(app):
    event = Event.create(url_id=1, user_id=1, event_type="click", details="not json")
    assert event.get_details() == {}


def test_event_get_details_none(app):
    event = Event.create(url_id=1, user_id=1, event_type="click", details=None)
    assert event.get_details() == {}
