from __future__ import annotations

import pytest
from sqlalchemy.orm import Session

from app.models import Severity
from app.repositories.incident_repository import IncidentRepository
from app.services.incident_service import DomainError, IncidentService


def make_service(db_session: Session) -> IncidentService:
    return IncidentService(IncidentRepository(db_session))


def test_assign_owner_persists(db_session: Session) -> None:
    service = make_service(db_session)
    incident = service.create_incident("Login latency", "", Severity.P2)

    updated = service.assign_owner(incident.id, "steven")

    assert updated.owner == "steven"


def test_assign_owner_rejects_blank_owner(db_session: Session) -> None:
    service = make_service(db_session)
    incident = service.create_incident("Login latency", "", Severity.P2)

    with pytest.raises(DomainError):
        service.assign_owner(incident.id, "   ")


def test_assign_owner_raises_for_missing_incident(db_session: Session) -> None:
    service = make_service(db_session)

    with pytest.raises(LookupError):
        service.assign_owner("does-not-exist", "steven")
