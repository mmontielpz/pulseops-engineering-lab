# PulseOps

A lightweight internal incident/support operations system. Built as the
hands-on lab for **AI Engineering with Claude Code**.

PulseOps is intentionally small: a React + TypeScript frontend, a FastAPI
backend, and SQLite for persistence. It ships ~65% complete - incident
listing, detail, and creation work today. Assignment, status workflow, and
the audit timeline are workshop slices (see `ACTIVE_SLICE.md` and
`docs/slices/`).

## Quickstart

```bash
git clone <repo>
cd pulseops
make bootstrap
make verify
```

`make bootstrap` creates a Python virtualenv (`backend/.venv`) and installs
frontend dependencies. `make verify` runs the full verification suite:
backend lint + type check + tests, frontend lint + tests + build.

To run the app locally:

```bash
make dev
```

This starts the backend on `http://localhost:8000` and the frontend on
`http://localhost:5173` (which proxies API calls to the backend).

## Architecture

```
Frontend (React + TS)
      |
   REST API (FastAPI)
      |
  Service layer      <- business rules live here
      |
  Repository layer    <- persistence only, no business rules
      |
   SQLite
```

Backend layout:

```
backend/
  app/
    api/            FastAPI routers (HTTP concerns only)
    services/        business rules (state machine, validation)
    repositories/    persistence (no business rules)
    models.py        SQLAlchemy ORM models
    schemas.py        Pydantic request/response shapes
    db.py            engine/session/init
    seed.py          representative sample data
  tests/
```

Frontend layout:

```
frontend/src/
  api/        typed fetch wrappers
  types/      shared TypeScript types (mirrors backend schema)
  pages/      IncidentList, IncidentDetail, NewIncident
```

## Commands

| Command | What it does |
|---|---|
| `make bootstrap` | Install backend + frontend dependencies |
| `make verify` | Lint, type-check, test, and build everything |
| `make dev` | Run backend + frontend dev servers |
| `make seed` | Populate the database with representative incidents |
| `make clean` | Remove local DB file and frontend build output |

## Project memory

This repository uses a deliberately lightweight memory model for the
workshop - see `CLAUDE.md` for stable project rules and `ACTIVE_SLICE.md`
for the current task in progress. Git history is the verified record of
what actually happened.

## Domain rules

See `CLAUDE.md` for the incident status lifecycle and invariants enforced
by the service layer.
