from app.models.event import Event


def test_list_events(client):
    Event.create(url_id=1, user_id=1, event_type="click")
    r = client.get("/events")
    assert r.status_code == 200
    data = r.get_json()
    assert len(data) == 1
    assert data[0]["event_type"] == "click"
