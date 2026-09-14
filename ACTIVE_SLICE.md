# ACTIVE SLICE

## Objective

Add incident ownership: an incident can be assigned to an owner, and the
assignment is visible end-to-end (database to UI).

## Relevant Context

- backend/app/models.py (Incident.owner already exists)
- backend/app/repositories/incident_repository.py
- backend/app/services/incident_service.py
- backend/app/api/incidents.py
- frontend/src/pages/IncidentDetail.tsx
- frontend/src/api/incidents.ts

## Scope

PATCH /incidents/{id}/assign, service method, frontend assignment control.

## Constraints

No status/lifecycle logic. No audit timeline. Validation in service layer only.

## Acceptance Criteria

- Assignment persists via API
- Empty/whitespace owner rejected (422)
- Frontend can assign and see it persist
- Existing tests pass unmodified
- make verify passes

## Verification

make verify

## Current State / Handoff

S001 complete and verified.

- `make verify`: PASS (backend 16 tests, frontend 5 tests, lint clean,
  types clean, build clean). Took 3 verification attempts: 2 rework
  iterations for real findings (ruff: unused import + `assert False`
  anti-pattern; tsc: unused mock parameter), 1 final clean pass.
- Runtime smoke test: created an incident, assigned an owner via
  `PATCH /incidents/{id}/assign`, confirmed persistence via `GET`,
  confirmed whitespace-only owner is rejected with 422.
- Next: S002 (`docs/slices/S002-STATUS-WORKFLOW.md`).
