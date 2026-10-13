


#!/usr/bin/env bash
set -e



cd "$(dirname "$0")"

# Check required tools
if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: Python 3 is not installed."
    exit 1
fi

if ! python3 -m venv --help >/dev/null 2>&1; then
    echo "Error: Python venv is missing. Install python3-venv."
    exit 1
fi

# Create virtual environment if needed
if [ ! -f ".venv/bin/python" ]; then
    python3 -m venv .venv
fi


# Install dependencies
.venv/bin/python -m pip install -r requirements.txt

# Set up database
.venv/bin/python manage.py migrate --noinput

# Start application
echo "Stat Lab running at http://127.0.0.1:8000/"
exec .venv/bin/python manage.py runserver 0.0.0.0:8000