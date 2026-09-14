# S001 - Incident Assignment

## Objective

Add incident ownership: an incident can be assigned to an owner, and the
assignment is visible end-to-end (database to UI).

## Relevant Context

- `backend/app/models.py` - `Incident.owner` field already exists
  (nullable), unused by any endpoint yet.
- `backend/app/repositories/incident_repository.py` - has `save()` for
  persisting a mutated incident.
- `backend/app/services/incident_service.py` - add assignment logic here.
- `backend/app/api/incidents.py` - add the new endpoint here.
- `frontend/src/pages/IncidentDetail.tsx` - add the assignment control
  here.
- `frontend/src/api/incidents.ts` - add the client call here.

You do not need to read the frontend list page, the NewIncident form, or
the seed script - none of them change for this slice.

## Scope

- New endpoint: `PATCH /incidents/{id}/assign` accepting `{"owner": str}`.
- Service method `assign_owner(incident_id, owner)` that validates and
  persists the change.
- Frontend: an "Assign" control on the incident detail page that calls
  the new endpoint and reflects the result without a full page reload.

## Constraints

- Do not modify the incident creation or listing behavior.
- Do not modify the status field or add status-transition logic - that
  is S002.
- Do not add the audit-timeline / IncidentEvent model - that is S003.
- Owner assignment logic belongs in the service layer, not the API
  layer or the frontend.

## Acceptance Criteria

- An incident can be assigned to a named owner via the API.
- Assignment persists (a subsequent `GET` reflects the new owner).
- An empty or whitespace-only owner is rejected with a 422 and a clear
  error message.
- The frontend detail page shows the current owner and lets you change
  it.
- All existing tests continue to pass unmodified.
- `make verify` passes.

## Verification

```
make verify
```

Manual smoke test:
```
make dev
# open the app, click an incident, assign an owner, confirm it persists on reload
```

## Stop Condition

Stop once `make verify` passes and the acceptance criteria above are
demonstrated. Do not start S002.

## Current State / Handoff

(Fill in during execution - see `ACTIVE_SLICE.md`.)
