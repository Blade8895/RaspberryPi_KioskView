#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"
source .venv/bin/activate

WORKERS="${GUNICORN_WORKERS:-2}"
THREADS="${GUNICORN_THREADS:-4}"
TIMEOUT="${GUNICORN_TIMEOUT:-60}"

exec gunicorn \
  --bind 0.0.0.0:5000 \
  --workers "$WORKERS" \
  --worker-class gthread \
  --threads "$THREADS" \
  --timeout "$TIMEOUT" \
  --graceful-timeout 15 \
  --keep-alive 2 \
  app:app
