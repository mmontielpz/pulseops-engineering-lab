"""Domain/service layer for incidents.

This is where business rules live. As of the workshop starting commit,
the only rule enforced is basic input validation on creation - the
status lifecycle, ownership requirements, and audit trail are added by
workshop slices S001-S003.
"""
from __future__ import annotations

from app.models import Incident, Severity, Status
from app.repositories.incident_repository import IncidentRepository


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
        incident.owner = owner.strip()
        return self.repo.save(incident)
