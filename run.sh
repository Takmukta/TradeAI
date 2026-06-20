#!/bin/bash
set -e

# Load .env if it exists
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "ERROR: ANTHROPIC_API_KEY is not set."
  echo "Copy .env.example to .env and add your key."
  exit 1
fi

echo "Installing dependencies..."
pip install -r requirements.txt -q

echo "Starting TradeAI on http://localhost:8080"
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
