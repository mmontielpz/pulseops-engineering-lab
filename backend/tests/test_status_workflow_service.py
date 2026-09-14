from __future__ import annotations

import pytest
from sqlalchemy.orm import Session

from app.models import Severity, Status
from app.repositories.incident_repository import IncidentRepository
from app.services.incident_service import DomainError, IncidentService


def make_service(db_session: Session) -> IncidentService:
    return IncidentService(IncidentRepository(db_session))


def test_valid_transition_open_to_investigating(db_session: Session) -> None:
    service = make_service(db_session)
    incident = service.create_incident("Email worker stopped", "", Severity.P3)

    updated = service.change_status(incident.id, Status.INVESTIGATING)

    assert updated.status == Status.INVESTIGATING


def test_full_lifecycle_in_order(db_session: Session) -> None:
    service = make_service(db_session)
    incident = service.create_incident("Email worker stopped", "", Severity.P3)

    service.change_status(incident.id, Status.INVESTIGATING)
    service.change_status(incident.id, Status.RESOLVED)
    final = service.change_status(incident.id, Status.CLOSED)

    assert final.status == Status.CLOSED


def test_rejects_skipping_states_open_to_closed(db_session: Session) -> None:
    """Negative path: OPEN -> CLOSED directly must be rejected, proving the
    state machine actually enforces order rather than just accepting any
    status value."""
    service = make_service(db_session)
    incident = service.create_incident("Email worker stopped", "", Severity.P3)

    with pytest.raises(DomainError):
        service.change_status(incident.id, Status.CLOSED)

    # and the incident must be unchanged
    unchanged = service.get_incident(incident.id)
    assert unchanged is not None
    assert unchanged.status == Status.OPEN


def test_rejects_moving_backwards(db_session: Session) -> None:
    service = make_service(db_session)
    incident = service.create_incident("Email worker stopped", "", Severity.P3)
    service.change_status(incident.id, Status.INVESTIGATING)

    with pytest.raises(DomainError):
        service.change_status(incident.id, Status.OPEN)


def test_p1_without_owner_cannot_enter_investigating(db_session: Session) -> None:
    """Negative path proving the ownership invariant is enforced, not just
    documented."""
    service = make_service(db_session)
    incident = service.create_incident("Payment API failing", "", Severity.P1)

    with pytest.raises(DomainError):
        service.change_status(incident.id, Status.INVESTIGATING)

    unchanged = service.get_incident(incident.id)
    assert unchanged is not None
    assert unchanged.status == Status.OPEN


def test_p1_with_owner_can_enter_investigating(db_session: Session) -> None:
    service = make_service(db_session)
    incident = service.create_incident("Payment API failing", "", Severity.P1)
    service.assign_owner(incident.id, "mike")

    updated = service.change_status(incident.id, Status.INVESTIGATING)

    assert updated.status == Status.INVESTIGATING


def test_p2_without_owner_can_enter_investigating(db_session: Session) -> None:
    """The ownership invariant is P1-specific - P2 and below should not be
    blocked. This test would fail if the rule were implemented too broadly."""
    service = make_service(db_session)
    incident = service.create_incident("Login latency", "", Severity.P2)

    updated = service.change_status(incident.id, Status.INVESTIGATING)

    assert updated.status == Status.INVESTIGATING
