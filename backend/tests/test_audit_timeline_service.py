from __future__ import annotations

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import EventType, IncidentEvent, Severity, Status
from app.repositories.incident_repository import IncidentRepository
from app.services.incident_service import IncidentService


def make_service(db_session: Session) -> IncidentService:
    return IncidentService(IncidentRepository(db_session))


def test_assignment_creates_event(db_session: Session) -> None:
    service = make_service(db_session)
    incident = service.create_incident("Login latency", "", Severity.P2)

    service.assign_owner(incident.id, "steven")

    events = service.list_events(incident.id)
    assert len(events) == 1
    assert events[0].event_type == EventType.ASSIGNED
    assert events[0].previous_value is None
    assert events[0].new_value == "steven"


def test_reassignment_records_previous_owner(db_session: Session) -> None:
    service = make_service(db_session)
    incident = service.create_incident("Login latency", "", Severity.P2)
    service.assign_owner(incident.id, "steven")

    service.assign_owner(incident.id, "priya")

    events = service.list_events(incident.id)
    assert len(events) == 2
    assert events[1].previous_value == "steven"
    assert events[1].new_value == "priya"


def test_status_change_creates_event(db_session: Session) -> None:
    service = make_service(db_session)
    incident = service.create_incident("Email worker stopped", "", Severity.P3)

    service.change_status(incident.id, Status.INVESTIGATING)

    events = service.list_events(incident.id)
    assert len(events) == 1
    assert events[0].event_type == EventType.STATUS_CHANGED
    assert events[0].previous_value == "OPEN"
    assert events[0].new_value == "INVESTIGATING"


def test_events_are_ordered_oldest_first(db_session: Session) -> None:
    service = make_service(db_session)
    incident = service.create_incident("Email worker stopped", "", Severity.P3)

    service.change_status(incident.id, Status.INVESTIGATING)
    service.assign_owner(incident.id, "priya")
    service.change_status(incident.id, Status.RESOLVED)

    events = service.list_events(incident.id)
    assert [e.event_type for e in events] == [
        EventType.STATUS_CHANGED,
        EventType.ASSIGNED,
        EventType.STATUS_CHANGED,
    ]


def test_atomic_failure_rolls_back_incident_change(db_session: Session) -> None:
    """This is the atomicity test the slice spec asks for: it must
    actually force the event-creation half of the write to fail, and
    prove the incident mutation did not silently persist anyway.

    A tautological version of this test would just check that a
    successful call produces both an incident update and an event -
    that's already covered above. This test instead breaks the second
    write on purpose (a NOT NULL violation on IncidentEvent.new_value)
    and confirms the transaction is all-or-nothing.
    """
    repo = IncidentRepository(db_session)
    service = make_service(db_session)
    incident = service.create_incident("Email worker stopped", "", Severity.P3)
    assert incident.status == Status.OPEN

    # Mutate the incident in memory, exactly like change_status does,
    # then pair it with a deliberately invalid event (new_value is
    # NOT NULL in the schema).
    incident.status = Status.INVESTIGATING
    broken_event = IncidentEvent(
        incident_id=incident.id,
        event_type=EventType.STATUS_CHANGED,
        previous_value="OPEN",
        new_value=None,  # type: ignore[arg-type]  # intentionally invalid
    )

    with pytest.raises(IntegrityError):
        repo.save_with_event(incident, broken_event)

    db_session.rollback()

    # Re-fetch from the same session to see what actually persisted.
    reloaded = repo.get(incident.id)
    assert reloaded is not None
    assert reloaded.status == Status.OPEN, (
        "incident status change leaked through even though the paired "
        "event write failed - the transaction was not atomic"
    )
    assert repo.list_events(incident.id) == []
