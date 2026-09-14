from __future__ import annotations

from fastapi.testclient import TestClient


def _create(client: TestClient) -> str:
    resp = client.post(
        "/incidents",
        json={"title": "Login latency", "description": "", "severity": "P2"},
    )
    return resp.json()["id"]


def test_events_endpoint_returns_events_in_order(client: TestClient) -> None:
    incident_id = _create(client)
    client.patch(f"/incidents/{incident_id}/status", json={"status": "INVESTIGATING"})
    client.patch(f"/incidents/{incident_id}/assign", json={"owner": "steven"})

    resp = client.get(f"/incidents/{incident_id}/events")

    assert resp.status_code == 200
    events = resp.json()
    assert len(events) == 2
    assert events[0]["event_type"] == "STATUS_CHANGED"
    assert events[1]["event_type"] == "ASSIGNED"


def test_events_endpoint_missing_incident_returns_404(client: TestClient) -> None:
    resp = client.get("/incidents/does-not-exist/events")

    assert resp.status_code == 404


def test_new_incident_has_no_events(client: TestClient) -> None:
    incident_id = _create(client)

    resp = client.get(f"/incidents/{incident_id}/events")

    assert resp.status_code == 200
    assert resp.json() == []
