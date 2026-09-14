"""Seed the database with representative incidents.

Run with: python -m app.seed
Safe to re-run: it only seeds when the incidents table is empty.
"""
from __future__ import annotations

from app.db import SessionLocal, init_db
from app.models import Incident, Severity, Status


def _sample_incidents() -> list[Incident]:
    return [
        Incident(
            title="Payment API failing",
            description="5xx errors spiking on POST /charge since ~11:55.",
            severity=Severity.P1,
            status=Status.OPEN,
            owner=None,
        ),
        Incident(
            title="Login latency",
            description="p95 login latency above 3s for EU traffic.",
            severity=Severity.P2,
            status=Status.INVESTIGATING,
            owner="steven",
        ),
        Incident(
            title="Email worker stopped",
            description="Background worker for transactional email stopped consuming.",
            severity=Severity.P2,
            status=Status.RESOLVED,
            owner="priya",
        ),
    ]


def seed() -> None:
    init_db()
    db = SessionLocal()
    try:
        if db.query(Incident).count() > 0:
            print("Database already has incidents - skipping seed.")
            return
        incidents = _sample_incidents()
        db.add_all(incidents)
        db.commit()
        print(f"Seeded {len(incidents)} incidents.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
