"""Domain/service layer for incidents.

This is where business rules live. As of the workshop starting commit,
the only rule enforced is basic input validation on creation - the
status lifecycle, ownership requirements, and audit trail are added by
workshop slices S001-S003.
"""
from __future__ import annotations

from app.models import EventType, Incident, IncidentEvent, Severity, Status
from app.repositories.incident_repository import IncidentRepository

# The lifecycle is linear: an incident can only move to the next state.
# No skipping (e.g. OPEN -> CLOSED directly is invalid).
_NEXT_VALID_STATUS: dict[Status, Status] = {
    Status.OPEN: Status.INVESTIGATING,
    Status.INVESTIGATING: Status.RESOLVED,
    Status.RESOLVED: Status.CLOSED,
}


class DomainError(Exception):
    """Raised when a request violates a business rule.

    The API layer translates this into an HTTP 422 response.
    """


class IncidentService:
    def __init__(self, repo: IncidentRepository) -> None:
        self.repo = repo

    def list_incidents(self) -> list[Incident]:
        return self.repo.list_all()

    def get_incident(self, incident_id: str) -> Incident | None:
        return self.repo.get(incident_id)

    def create_incident(
        self, title: str, description: str, severity: Severity
    ) -> Incident:
        if not title.strip():
            raise DomainError("title must not be empty")
        incident = Incident(
            title=title.strip(),
            description=description,
            severity=severity,
            status=Status.OPEN,
        )
        return self.repo.add(incident)

    def assign_owner(self, incident_id: str, owner: str) -> Incident:
        if not owner.strip():
            raise DomainError("owner must not be empty")
        incident = self.repo.get(incident_id)
        if incident is None:
            raise LookupError(incident_id)

        previous_owner = incident.owner
        incident.owner = owner.strip()
        event = IncidentEvent(
            incident_id=incident.id,
            event_type=EventType.ASSIGNED,
            previous_value=previous_owner,
            new_value=incident.owner,
        )
        return self.repo.save_with_event(incident, event)

    def change_status(self, incident_id: str, new_status: Status) -> Incident:
        incident = self.repo.get(incident_id)
        if incident is None:
            raise LookupError(incident_id)

        expected_next = _NEXT_VALID_STATUS.get(incident.status)
        if expected_next is None or new_status != expected_next:
            raise DomainError(
                f"cannot move incident from {incident.status.value} to "
                f"{new_status.value}; the lifecycle is "
                "OPEN -> INVESTIGATING -> RESOLVED -> CLOSED"
            )

        if (
            new_status == Status.INVESTIGATING
            and incident.severity == Severity.P1
            and not incident.owner
        ):
            raise DomainError(
                "a P1 incident must have an owner before it can move to "
                "INVESTIGATING"
            )

        previous_status = incident.status
        incident.status = new_status
        event = IncidentEvent(
            incident_id=incident.id,
            event_type=EventType.STATUS_CHANGED,
            previous_value=previous_status.value,
            new_value=new_status.value,
        )
        return self.repo.save_with_event(incident, event)

    def list_events(self, incident_id: str) -> list[IncidentEvent]:
        return self.repo.list_events(incident_id)
