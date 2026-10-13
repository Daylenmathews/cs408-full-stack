
#!/usr/bin/env bash


set -euo pipefail

HOST=""
KEY=""

while getopts "h:i:" opt; do

    case "$opt" in
        h) HOST="$OPTARG" ;;
        i) KEY="$OPTARG" ;;
        *) exit 1 ;;
    esac
done

if [ -z "$HOST" ] || [ -z "$KEY" ]; then
    echo "Usage: ./deploy/deploy.sh -h PUBLIC_IP -i KEY_FILE"
    exit 1
fi

if [ ! -f "$KEY" ]; then

    echo "Error: SSH key not found: $KEY"
    exit 1
fi



ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "Checking Django..."
if [ -f .venv/bin/python ]; then

    .venv/bin/python manage.py check
elif command -v python3 >/dev/null 2>&1; then

    python3 manage.py check
else
    echo "Error: Python 3 is required."
    exit 1
fi

echo "Uploading Stat Lab..."

rsync -avz \
    --exclude='.git/' \
    --exclude='.venv/' \
    --exclude='db.sqlite3' \
    --exclude='.env' \
    --exclude='*.pem' \
    -e "ssh -i $KEY" \
    ./ "ubuntu@$HOST:/home/ubuntu/stat-lab/"

echo "Installing dependencies and restarting..."
ssh -i "$KEY" "ubuntu@$HOST" '
    set -e
    cd /home/ubuntu/stat-lab
    if [ ! -f .venv/bin/python ]; then
        python3 -m venv .venv
    fi
    .venv/bin/python -m pip install -r requirements.txt
    .venv/bin/python manage.py migrate --noinput
    sudo systemctl restart stat-lab.service
'

echo "Checking website..."
curl --fail --retry 5 --retry-delay 3 "http://$HOST/"

echo "Deployment complete!"
echo "Open http://$HOST/"
