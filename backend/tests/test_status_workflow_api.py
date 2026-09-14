from __future__ import annotations

from fastapi.testclient import TestClient


def _create(client: TestClient, severity: str = "P3") -> str:
    resp = client.post(
        "/incidents",
        json={"title": "Email worker stopped", "description": "", "severity": severity},
    )
    return resp.json()["id"]


def test_change_status_via_api(client: TestClient) -> None:
    incident_id = _create(client)

    resp = client.patch(f"/incidents/{incident_id}/status", json={"status": "INVESTIGATING"})

    assert resp.status_code == 200
    assert resp.json()["status"] == "INVESTIGATING"


def test_change_status_rejects_invalid_transition(client: TestClient) -> None:
    incident_id = _create(client)

    resp = client.patch(f"/incidents/{incident_id}/status", json={"status": "CLOSED"})

    assert resp.status_code == 422


def test_change_status_rejects_p1_without_owner(client: TestClient) -> None:
    incident_id = _create(client, severity="P1")

    resp = client.patch(f"/incidents/{incident_id}/status", json={"status": "INVESTIGATING"})

    assert resp.status_code == 422


def test_change_status_allows_p1_with_owner(client: TestClient) -> None:
    incident_id = _create(client, severity="P1")
    client.patch(f"/incidents/{incident_id}/assign", json={"owner": "mike"})

    resp = client.patch(f"/incidents/{incident_id}/status", json={"status": "INVESTIGATING"})

    assert resp.status_code == 200


def test_change_status_missing_incident_returns_404(client: TestClient) -> None:
    resp = client.patch("/incidents/does-not-exist/status", json={"status": "INVESTIGATING"})

    assert resp.status_code == 404
