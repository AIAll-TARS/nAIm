#!/bin/sh
set -e

echo "Running DB seed (creates tables + initial data)..."
python -m app.seed

echo "Starting API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
