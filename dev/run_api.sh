#!/usr/bin/env bash
# Run demoGauntlet FastAPI backend on port 5003
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Activate venv if present
if [ -d ".venv" ]; then
    source ".venv/bin/activate"
elif [ -d "venv" ]; then
    source "venv/bin/activate"
fi

echo "Starting demoGauntlet API on http://127.0.0.1:5003"
exec uvicorn backend.main:app --host 127.0.0.1 --reload --port 5003
