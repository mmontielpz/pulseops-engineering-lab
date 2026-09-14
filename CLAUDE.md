# CLAUDE.md

Stable project guidance for PulseOps. This file changes rarely - current
task state belongs in `ACTIVE_SLICE.md`, not here.

## What PulseOps is

A small internal incident-management system. Frontend (React + TS) talks
to a REST API (FastAPI) backed by SQLite. Business rules live in the
service layer, not the API layer, the repository layer, or the frontend.

## Architecture (do not violate without an explicit slice asking for it)

```
frontend (React + TS)  ->  API (FastAPI routers)  ->  service (business rules)
                                                    ->  repository (persistence only)
                                                    ->  SQLite
```

- **API layer** (`backend/app/api/`): HTTP concerns only - request/response
  shapes, status codes. No business rules.
- **Service layer** (`backend/app/services/`): all business rules and
  invariants live here. Raises `DomainError` on violation; the API layer
  translates that to HTTP 422.
- **Repository layer** (`backend/app/repositories/`): persistence only.
  No validation, no business rules.
- Domain rules must not be duplicated independently across layers. If a
  rule needs to be checked, it is checked once, in the service layer.

## Canonical commands

| Purpose | Command |
|---|---|
| Install everything | `make bootstrap` |
| Full verification (lint + types + tests + build) | `make verify` |
| Run locally | `make dev` |
| Seed sample data | `make seed` |

Backend-only, from `backend/` with the venv active:
`ruff check .`, `mypy app`, `pytest -q`

Frontend-only, from `frontend/`:
`npm run lint`, `npm run test`, `npm run build`

## Verification contract

**Generated is not done.** A change is done when:

1. `make verify` passes (lint, type check, backend tests, frontend
   lint/tests, frontend build all green).
2. The diff matches the current slice's scope - no unrelated files
   touched.
3. Acceptance criteria in `ACTIVE_SLICE.md` are met and can be
   demonstrated, not just asserted.

The agent can claim success. `make verify` decides whether the
repository agrees.

## Domain rules (incident lifecycle)

Status lifecycle is linear, no skipping:

```
OPEN -> INVESTIGATING -> RESOLVED -> CLOSED
```

Invariants (enforced in the service layer):

- A status transition must follow the lifecycle order above. `OPEN ->
  CLOSED` directly is invalid.
- A P1 incident must have an owner assigned before it can move to
  INVESTIGATING.
- Meaningful changes (status transitions, assignment) should be
  traceable after the fact - see `ACTIVE_SLICE.md` if this is the
  current slice.

## Safety & permission boundaries

**MAY:**
- Inspect any file in the repository.
- Edit application code within the current slice's scope.
- Run `make verify` and its component commands.
- Add tests that exercise new or changed behavior.

**MUST:**
- Preserve existing passing tests unless the slice explicitly changes
  that behavior.
- Inspect relevant existing tests and code before modifying shared
  logic (service layer, models).
- Run `make verify` before declaring a slice complete.
- Keep the diff scoped to the current slice.

**MUST NOT without approval:**
- Expose secrets or credentials (none exist in this repo today - keep
  it that way).
- Modify files outside the current slice's stated scope.
- Rewrite large unrelated areas of the codebase.
- Bypass or delete a failing test to make verification pass.
- Weaken an invariant to make a feature easier to implement.

**MUST ASK before:**
- Destructive shell operations (`rm -rf`, force-push, resetting the
  database file outside `make clean`).
- Adding or upgrading dependencies not already in
  `backend/requirements.txt` or `frontend/package.json`.
- Any schema change that could destroy existing data outside normal
  `create_all` additive changes.
- Broad architectural changes (e.g., introducing a new persistence
  layer, changing the layering model above).

## What NOT to do

- Do not put business logic in `backend/app/api/` or
  `backend/app/repositories/`.
- Do not duplicate a validation rule in the frontend as the source of
  truth - the backend service layer is authoritative. Frontend-side
  checks are a UX nicety, not enforcement.
- Do not add a migration framework, message queue, cache layer, or
  second database for this workshop. If a slice seems to need one,
  re-scope the slice instead.
