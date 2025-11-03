#!/bin/bash

# Run script for LLM Chat API
# Handles SSL certificate check and starts the server

# Check if SSL certificates exist
SSL_CERT="${SCRIPT_DIR}/ssl/server.crt"
SSL_KEY="${SCRIPT_DIR}/ssl/server.key"

# Use virtual environment if it exists, otherwise system Python
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ -f "$SCRIPT_DIR/venv/bin/activate" ]; then
    source "$SCRIPT_DIR/venv/bin/activate"
    PYTHON_CMD=python
    echo "Using virtual environment"
else
    # Detect Python command (works in both Docker and local)
    if command -v python3 &> /dev/null; then
        PYTHON_CMD=python3
    elif command -v python &> /dev/null; then
        PYTHON_CMD=python
    else
        echo "Error: Python not found!"
        exit 1
    fi
fi

if [ -f "$SSL_CERT" ] && [ -f "$SSL_KEY" ]; then
    echo "SSL certificates found. Starting with HTTPS..."
    $PYTHON_CMD -m uvicorn app.main:app --host 0.0.0.0 --port 8000 \
        --ssl-certfile "$SSL_CERT" \
        --ssl-keyfile "$SSL_KEY"
else
    echo "SSL certificates not found. Starting with HTTP..."
    echo "To enable HTTPS, run: ./ssl/generate-cert.sh"
    $PYTHON_CMD -m uvicorn app.main:app --host 0.0.0.0 --port 8000
fi

