from __future__ import annotations

from fastapi.testclient import TestClient


def _create_incident(client: TestClient) -> str:
    resp = client.post(
        "/incidents", json={"title": "Login latency", "description": "", "severity": "P2"}
    )
    return resp.json()["id"]


def test_assign_owner_via_api(client: TestClient) -> None:
    incident_id = _create_incident(client)

    resp = client.patch(f"/incidents/{incident_id}/assign", json={"owner": "steven"})

    assert resp.status_code == 200
    assert resp.json()["owner"] == "steven"

    resp2 = client.get(f"/incidents/{incident_id}")
    assert resp2.json()["owner"] == "steven"


def test_assign_owner_rejects_empty_string(client: TestClient) -> None:
    incident_id = _create_incident(client)

    resp = client.patch(f"/incidents/{incident_id}/assign", json={"owner": ""})

    assert resp.status_code == 422


def test_assign_owner_rejects_whitespace_only(client: TestClient) -> None:
    incident_id = _create_incident(client)

    resp = client.patch(f"/incidents/{incident_id}/assign", json={"owner": "   "})

    assert resp.status_code == 422


def test_assign_owner_missing_incident_returns_404(client: TestClient) -> None:
    resp = client.patch("/incidents/does-not-exist/assign", json={"owner": "steven"})

    assert resp.status_code == 404
