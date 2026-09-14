"""Pydantic schemas (API-facing shapes). Kept separate from ORM models
so the API contract can evolve independently of persistence.
"""
from __future__ import annotations

import datetime

from pydantic import BaseModel, Field

from app.models import EventType, Severity, Status


class IncidentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    severity: Severity


class AssignOwnerRequest(BaseModel):
    owner: str = Field(min_length=1, max_length=100)


class ChangeStatusRequest(BaseModel):
    status: Status


class IncidentOut(BaseModel):
    id: str
    title: str
    description: str
    severity: Severity
    status: Status
    owner: str | None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}


class IncidentEventOut(BaseModel):
    id: str
    incident_id: str
    event_type: EventType
    previous_value: str | None
    new_value: str
    created_at: datetime.datetime

    model_config = {"from_attributes": True}
