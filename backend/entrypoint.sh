#!/bin/bash
set -e

# Run migrations
echo "Running database migrations..."
alembic upgrade head

# Check for seeding flags
if [ "$RESET_DB" = "true" ]; then
    echo "Resetting and seeding database..."
    python seed_data.py --reset
elif [ "$SEED_DB" = "true" ]; then
    echo "Seeding database..."
    python seed_data.py
fi

# Check if a command was passed as arguments
if [ $# -gt 0 ]; then
    echo "Executing command: $@"
    exec "$@"
fi

# Start the application
echo "Starting application..."
exec uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
