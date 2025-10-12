#!/bin/bash

# Start the Flask application with Gunicorn

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Get port from environment or use default
PORT=${FLASK_PORT:-8000}

# Number of workers (recommended: 2-4 x NUM_CORES)
WORKERS=${WORKERS:-4}

# Timeout in seconds
TIMEOUT=${TIMEOUT:-120}

echo "Starting Gunicorn server on port $PORT with $WORKERS workers..."

# Run Gunicorn
gunicorn wsgi:app \
    --bind 0.0.0.0:$PORT \
    --workers $WORKERS \
    --timeout $TIMEOUT \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --reload

