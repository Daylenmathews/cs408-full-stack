


#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

# Check Python
if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: Python 3 is not installed."
    exit 1
fi

# Create virtual environment
if [ ! -f ".venv/bin/python" ]; then
    python3 -m venv .venv
fi

# Install dependencies
.venv/bin/python -m pip install -r requirements.txt

# Set up database
.venv/bin/python manage.py migrate --noinput

# Import NFL player data
echo "Updating NFL player data..."
.venv/bin/python manage.py update_nfl --team sea

# Start Django
echo "Starting Stat Lab..."
exec .venv/bin/python manage.py runserver 0.0.0.0:8000