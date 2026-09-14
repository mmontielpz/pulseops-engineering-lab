#!/usr/bin/env bash
# Runs the backend and frontend dev servers together.
# Ctrl-C stops both.
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$(pwd)"

if [ -x "$ROOT/backend/.venv/bin/python" ]; then
  PY="$ROOT/backend/.venv/bin/python"
else
  PY=python3
fi

cleanup() {
  echo "==> Stopping dev servers"
  kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
}
trap cleanup EXIT

echo "==> Starting backend (http://localhost:8000)"
(cd "$ROOT/backend" && "$PY" -m app.seed && "$PY" -m uvicorn app.main:app --reload --port 8000) &
BACKEND_PID=$!

echo "==> Starting frontend (http://localhost:5173)"
(cd "$ROOT/frontend" && npm run dev) &
FRONTEND_PID=$!

wait
