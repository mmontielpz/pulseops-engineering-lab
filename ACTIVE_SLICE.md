# ACTIVE SLICE

## Objective

Record meaningful incident changes (assignment, status transitions) as an
immutable, ordered timeline, atomically with the change itself.

## Relevant Context

- backend/app/models.py (add IncidentEvent here)
- backend/app/services/incident_service.py (assign_owner, change_status)
- backend/app/repositories/incident_repository.py
- backend/app/api/incidents.py (add GET /incidents/{id}/events)
- frontend/src/pages/IncidentDetail.tsx

## Scope

IncidentEvent model. Event creation in same transaction as the incident
update for both assign_owner and change_status. Timeline endpoint. Frontend
timeline UI.

## Constraints

Events immutable through public API. No migration framework - extend
models.py + create_all. Don't change S001/S002 request/response shapes.

## Acceptance Criteria

- Assignment creates ASSIGNED event with previous/new owner
- Status change creates STATUS_CHANGED event with previous/new status
- Timeline endpoint returns events oldest-first
- A REAL atomicity test: force the event-creation half to fail and
  assert the incident update was rolled back
- Existing S001/S002 tests pass unmodified
- make verify passes

## Verification

make verify

## Current State / Handoff

In progress.
