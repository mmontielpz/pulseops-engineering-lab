# S002 - Status Workflow & Domain Rules

## Objective

Implement the incident status lifecycle as an enforced state machine, not
just a free-form field.

## Relevant Context

- `CLAUDE.md` - the lifecycle and invariants are already documented
  there (read this first - don't re-derive the rules from scratch).
- `backend/app/models.py` - `Status` enum already defines the four
  states.
- `backend/app/services/incident_service.py` - `assign_owner` from S001
  is here; status-transition logic belongs alongside it.
- `backend/app/api/incidents.py` - existing endpoint patterns to follow
  for the new status endpoint.
- `frontend/src/pages/IncidentDetail.tsx` - the assignment control from
  S001 is here; the status control belongs alongside it.

## Scope

- New endpoint: `PATCH /incidents/{id}/status` accepting
  `{"status": str}`.
- Service method that validates the transition against the lifecycle
  (`OPEN -> INVESTIGATING -> RESOLVED -> CLOSED`, no skipping) and the
  ownership invariant (a P1 incident needs an owner before it can enter
  INVESTIGATING).
- Frontend: a status control on the incident detail page.

## Constraints

- The lifecycle order and the P1-needs-owner rule are documented in
  `CLAUDE.md` - do not invent additional rules beyond what's specified
  there without flagging it.
- Do not add the audit-timeline / IncidentEvent model yet - that is
  S003. A status change in this slice does not need to be recorded
  anywhere beyond the incident's own `status` field.
- Validation belongs in the service layer.

## Acceptance Criteria

- Valid transitions succeed (`OPEN -> INVESTIGATING`, etc., in order).
- Invalid transitions are rejected with 422 and a clear message (e.g.
  `OPEN -> CLOSED` directly).
- A P1 incident without an owner cannot move to INVESTIGATING; the
  same transition succeeds once an owner is assigned.
- Existing tests (including S001's) continue to pass unmodified.
- At least one new test exercises a rejected invalid transition, and at
  least one exercises the P1-ownership invariant being enforced.
- `make verify` passes.

## Verification

```
make verify
```

Include a negative-path test that proves the rejection actually
happens - not just a test that the happy path works.

## Stop Condition

Stop once `make verify` passes and the acceptance criteria above are
demonstrated. Do not start S003.

## Current State / Handoff

(Fill in during execution - see `ACTIVE_SLICE.md`.)
