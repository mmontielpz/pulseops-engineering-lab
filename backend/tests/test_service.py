from __future__ import annotations

import pytest
from sqlalchemy.orm import Session

from app.models import Severity, Status
from app.repositories.incident_repository import IncidentRepository
from app.services.incident_service import DomainError, IncidentService


def make_service(db_session: Session) -> IncidentService:
    return IncidentService(IncidentRepository(db_session))


def test_create_incident_persists_with_open_status(db_session: Session) -> None:
    service = make_service(db_session)

    incident = service.create_incident("Payment API failing", "5xx spike", Severity.P1)

    assert incident.id
    assert incident.status == Status.OPEN
    assert incident.owner is None


def test_create_incident_rejects_empty_title(db_session: Session) -> None:
    service = make_service(db_session)

    with pytest.raises(DomainError):
        service.create_incident("   ", "no title", Severity.P2)


def test_list_incidents_returns_created_incidents(db_session: Session) -> None:
    service = make_service(db_session)
    service.create_incident("Login latency", "", Severity.P2)
    service.create_incident("Email worker stopped", "", Severity.P3)

    incidents = service.list_incidents()

    assert len(incidents) == 2


def test_get_incident_returns_none_when_missing(db_session: Session) -> None:
    service = make_service(db_session)

    assert service.get_incident("does-not-exist") is None
