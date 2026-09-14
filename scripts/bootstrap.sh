#!/usr/bin/env bash
# Installs backend and frontend dependencies. Idempotent.
#
# Creates a Python virtualenv at backend/.venv so PulseOps doesn't fight
# system-managed Python installs. Re-run any time; it's safe.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> Backend: creating virtualenv (backend/.venv) if needed"
if [ ! -d backend/.venv ]; then
  python3 -m venv backend/.venv
fi

echo "==> Backend: installing Python dependencies"
backend/.venv/bin/pip install --quiet --upgrade pip
backend/.venv/bin/pip install --quiet -r backend/requirements.txt

echo "==> Frontend: installing npm dependencies"
(cd frontend && npm install --silent)

echo "==> Bootstrap complete. Activate the backend venv with:"
echo "      source backend/.venv/bin/activate"
