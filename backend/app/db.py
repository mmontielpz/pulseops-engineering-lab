"""Database engine and session management.

PulseOps uses SQLite for workshop simplicity. The engine is created once
per process; sessions are short-lived and created per request/operation.
"""
from __future__ import annotations

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DB_PATH = os.environ.get("PULSEOPS_DB_PATH", "pulseops.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# check_same_thread=False is required for SQLite when used across FastAPI's
# threaded request handling; each request still gets its own Session.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a request-scoped session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables. Idempotent - safe to call on every startup.

    PulseOps intentionally has no migration framework (e.g. Alembic) for
    workshop simplicity. Slice S003 adds a new table (IncidentEvent) by
    extending the models in this file and relying on create_all, which is
    fine for SQLite + a workshop but is explicitly NOT a production-grade
    migration story. This tradeoff is documented in CLAUDE.md.
    """
    Base.metadata.create_all(bind=engine)
