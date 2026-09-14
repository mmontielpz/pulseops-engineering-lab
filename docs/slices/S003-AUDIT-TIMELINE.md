# S003 - Incident Audit Timeline

## Objective

Record meaningful incident changes (status transitions, assignment) as
an immutable, ordered timeline, atomically with the change itself.

## Relevant Context

- `backend/app/models.py` - add `IncidentEvent` here (does not exist
  yet).
- `backend/app/services/incident_service.py` - `assign_owner` (S001) and
  the status-transition method (S002) are the two places that need to
  also create an event.
- `backend/app/repositories/incident_repository.py` - persistence only;
  if event creation needs new persistence methods, add them here.
- `backend/app/api/incidents.py` - add a `GET /incidents/{id}/events`
  endpoint.
- `frontend/src/pages/IncidentDetail.tsx` - add a timeline section.

## The core engineering concern: atomicity

A naive implementation does this:

```python
incident.status = new_status
repo.save(incident)          # write 1
repo.add(IncidentEvent(...))  # write 2
```

If the process dies between write 1 and write 2, the incident's status
changed but no event recorded why - the audit trail is now lying by
omission. The incident update and its event must succeed or fail
together, inside one transaction boundary.

## Scope

- `IncidentEvent` model: id, incident_id, event_type, previous_value,
  new_value, created_at.
- Both `assign_owner` and the status-transition method must create a
  corresponding `IncidentEvent` in the same transaction as the incident
  update.
- New endpoint: `GET /incidents/{id}/events`, ordered oldest-first.
- Frontend: a timeline component on the incident detail page.

## Constraints

- Events are immutable through the public API - there is no update or
  delete endpoint for events.
- Do not change the S001/S002 endpoints' request or response shapes -
  only their internal implementation gains event creation.
- This is still SQLite with `create_all` - no migration framework. Add
  the table by extending `models.py`; existing incident rows must
  continue to work unmodified (no backfill required, since there is no
  prior event history to backfill).

## Acceptance Criteria

- Assigning an owner creates an `ASSIGNED` event with the previous and
  new owner values.
- A status transition creates a `STATUS_CHANGED` event with the
  previous and new status values.
- The timeline endpoint returns events in creation order.
- A test proves atomicity: force the event-creation half of the
  operation to fail and assert the incident update was rolled back
  (not partially applied).
- Existing S001 and S002 tests continue to pass unmodified.
- `make verify` passes.

## Verification

```
make verify
```

The atomicity test is the one that matters most here - a passing test
suite that never actually exercises the failure path does not prove
atomicity, it just proves the happy path works twice.

## Stop Condition

Stop once `make verify` passes, the atomicity test is real (not
tautological), and the acceptance criteria above are demonstrated.

## Current State / Handoff

(Fill in during execution - see `ACTIVE_SLICE.md`.)
