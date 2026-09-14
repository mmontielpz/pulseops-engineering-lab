# ACTIVE SLICE

## Objective

Implement the incident status lifecycle as an enforced state machine.

## Relevant Context

- CLAUDE.md (lifecycle + invariants already documented there)
- backend/app/models.py (Status enum)
- backend/app/services/incident_service.py (assign_owner lives here)
- backend/app/api/incidents.py
- frontend/src/pages/IncidentDetail.tsx

## Scope

PATCH /incidents/{id}/status with transition validation; frontend status control.

## Constraints

Lifecycle: OPEN -> INVESTIGATING -> RESOLVED -> CLOSED, no skipping.
P1 incidents need an owner before entering INVESTIGATING.
No audit timeline yet (S003). Validation in service layer only.

## Acceptance Criteria

- Valid transitions succeed in order
- Invalid transitions (e.g. OPEN -> CLOSED) rejected with 422
- P1 without owner cannot enter INVESTIGATING; succeeds once owner assigned
- Existing tests pass unmodified
- At least one negative-path test per rule
- make verify passes

## Verification

make verify

## Current State / Handoff

S002 complete and verified.

- `make verify`: PASS (backend 28 tests, frontend 5 tests, lint clean,
  types clean, build clean). Took 2 verification attempts: 1 rework
  iteration for a real ruff line-length finding, 1 clean pass.
- Runtime smoke test: confirmed OPEN->CLOSED rejected (422), P1 without
  owner rejected from entering INVESTIGATING (422), same P1 succeeds
  after assignment (200), and a full OPEN->INVESTIGATING->RESOLVED->
  CLOSED lifecycle succeeds on a P3 incident.
- Next: S003 (`docs/slices/S003-AUDIT-TIMELINE.md`).
