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

S003 complete and verified.

- `make verify`: PASS (backend 36 tests, frontend 5 tests, lint clean,
  types clean, build clean). Took 3 verification attempts: 2 rework
  iterations for real findings (ruff: blind `except Exception` in the
  atomicity test needed narrowing to `IntegrityError`; tsc: forgot to
  export the `IncidentEvent` type on the frontend, caught only at the
  build step, not by lint or tests), 1 clean pass.
- The atomicity test (`test_atomic_failure_rolls_back_incident_change`)
  genuinely forces an `IntegrityError` on the event write and asserts
  the paired incident mutation did not leak through - not a
  tautological test that only exercises the happy path.
- Runtime smoke test: assigned + transitioned a P1 incident via a live
  server, fetched `/incidents/{id}/events`, confirmed both events
  recorded in correct chronological order with correct previous/new
  values.
- Workshop slices S001-S003 are now complete. Next: the workshop's
  Context-Kill and failure-recovery exercises (see
  AICA-005-PULSEOPS-BENCHMARK.md once written), not a new slice.
