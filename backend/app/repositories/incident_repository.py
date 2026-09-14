"""Persistence layer for incidents.

Repositories talk to the database and nothing else. Business rules
(state machine validation, ownership requirements, etc.) belong in
app/services, not here.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Incident


class IncidentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(self) -> list[Incident]:
        stmt = select(Incident).order_by(Incident.created_at.desc())
        return list(self.db.execute(stmt).scalars().all())

    def get(self, incident_id: str) -> Incident | None:
        return self.db.get(Incident, incident_id)

    def add(self, incident: Incident) -> Incident:
        self.db.add(incident)
        self.db.commit()
        self.db.refresh(incident)
        return incident

    def save(self, incident: Incident) -> Incident:
        self.db.commit()
        self.db.refresh(incident)
        return incident
