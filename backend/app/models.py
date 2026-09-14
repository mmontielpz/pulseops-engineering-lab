"""ORM models for PulseOps.

Baseline (workshop starting commit) defines Incident only.
Slice S003 (Audit Timeline) extends this file with IncidentEvent.
"""
from __future__ import annotations

import datetime
import enum
import uuid

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Severity(enum.StrEnum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class Status(enum.StrEnum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


def _uuid() -> str:
    return uuid.uuid4().hex[:8]


def _now() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False, default="")
    severity: Mapped[Severity] = mapped_column(Enum(Severity), nullable=False)
    status: Mapped[Status] = mapped_column(
        Enum(Status), nullable=False, default=Status.OPEN
    )
    owner: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=_now
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now
    )


class EventType(enum.StrEnum):
    ASSIGNED = "ASSIGNED"
    STATUS_CHANGED = "STATUS_CHANGED"


class IncidentEvent(Base):
    """An immutable audit record of a meaningful incident change.

    Created in the same database transaction as the incident mutation it
    describes (see IncidentService) - see S003's slice spec for why that
    matters.
    """

    __tablename__ = "incident_events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    incident_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    event_type: Mapped[EventType] = mapped_column(Enum(EventType), nullable=False)
    previous_value: Mapped[str | None] = mapped_column(String, nullable=True)
    new_value: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=_now
    )
