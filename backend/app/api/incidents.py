from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.repositories.incident_repository import IncidentRepository
from app.schemas import AssignOwnerRequest, ChangeStatusRequest, IncidentCreate, IncidentOut
from app.services.incident_service import DomainError, IncidentService

router = APIRouter(prefix="/incidents", tags=["incidents"])


def get_service(db: Session = Depends(get_db)) -> IncidentService:
    return IncidentService(IncidentRepository(db))


@router.get("", response_model=list[IncidentOut])
def list_incidents(service: IncidentService = Depends(get_service)) -> list[IncidentOut]:
    return [IncidentOut.model_validate(i) for i in service.list_incidents()]


@router.get("/{incident_id}", response_model=IncidentOut)
def get_incident(
    incident_id: str, service: IncidentService = Depends(get_service)
) -> IncidentOut:
    incident = service.get_incident(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="incident not found")
    return IncidentOut.model_validate(incident)


@router.post("", response_model=IncidentOut, status_code=201)
def create_incident(
    payload: IncidentCreate, service: IncidentService = Depends(get_service)
) -> IncidentOut:
    try:
        incident = service.create_incident(
            payload.title, payload.description, payload.severity
        )
    except DomainError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return IncidentOut.model_validate(incident)


@router.patch("/{incident_id}/assign", response_model=IncidentOut)
def assign_owner(
    incident_id: str,
    payload: AssignOwnerRequest,
    service: IncidentService = Depends(get_service),
) -> IncidentOut:
    try:
        incident = service.assign_owner(incident_id, payload.owner)
    except DomainError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="incident not found") from exc
    return IncidentOut.model_validate(incident)


@router.patch("/{incident_id}/status", response_model=IncidentOut)
def change_status(
    incident_id: str,
    payload: ChangeStatusRequest,
    service: IncidentService = Depends(get_service),
) -> IncidentOut:
    try:
        incident = service.change_status(incident_id, payload.status)
    except DomainError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="incident not found") from exc
    return IncidentOut.model_validate(incident)
