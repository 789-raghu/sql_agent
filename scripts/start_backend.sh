#!/usr/bin/env bash
set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"
export PYTHONPATH="$PROJECT_DIR"

echo "Starting FastAPI Backend Server from $PROJECT_DIR..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
