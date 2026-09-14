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

In progress.
