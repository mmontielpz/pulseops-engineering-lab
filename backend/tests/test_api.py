from __future__ import annotations

from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_create_and_get_incident(client: TestClient) -> None:
    resp = client.post(
        "/incidents",
        json={"title": "Payment API failing", "description": "5xx spike", "severity": "P1"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "OPEN"
    assert body["owner"] is None

    resp2 = client.get(f"/incidents/{body['id']}")
    assert resp2.status_code == 200
    assert resp2.json()["title"] == "Payment API failing"


def test_create_incident_rejects_empty_title(client: TestClient) -> None:
    resp = client.post(
        "/incidents", json={"title": "   ", "description": "", "severity": "P2"}
    )
    assert resp.status_code == 422


def test_list_incidents(client: TestClient) -> None:
    client.post("/incidents", json={"title": "A", "description": "", "severity": "P3"})
    client.post("/incidents", json={"title": "B", "description": "", "severity": "P4"})

    resp = client.get("/incidents")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_get_missing_incident_returns_404(client: TestClient) -> None:
    resp = client.get("/incidents/does-not-exist")
    assert resp.status_code == 404
