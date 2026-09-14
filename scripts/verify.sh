#!/usr/bin/env bash
# Canonical verification path for PulseOps.
#
# Generated != Done. This is the one command that decides whether the
# repository agrees with a claim of "it works": lint, type checks,
# backend tests, frontend lint/tests, and a production build.
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$(pwd)"

if [ -x "$ROOT/backend/.venv/bin/python" ]; then
  BIN="$ROOT/backend/.venv/bin"
else
  BIN=""  # fall back to whatever is on PATH
fi

run_py() {
  if [ -n "$BIN" ]; then "$BIN/$1" "${@:2}"; else "$1" "${@:2}"; fi
}

echo "==> [1/6] Backend lint (ruff)"
(cd "$ROOT/backend" && run_py ruff check .)

echo "==> [2/6] Backend type check (mypy)"
(cd "$ROOT/backend" && PYTHONPATH=. run_py mypy app)

echo "==> [3/6] Backend tests (pytest)"
(cd "$ROOT/backend" && run_py pytest -q)

echo "==> [4/6] Frontend lint (oxlint)"
(cd "$ROOT/frontend" && npm run --silent lint)

echo "==> [5/6] Frontend tests (vitest)"
(cd "$ROOT/frontend" && npm run --silent test)

echo "==> [6/6] Frontend build (tsc + vite build)"
(cd "$ROOT/frontend" && npm run --silent build)

echo "==> Verification complete: PASS"
