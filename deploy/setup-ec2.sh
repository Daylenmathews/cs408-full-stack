
#!/usr/bin/env bash
set -e

# Must be run as root
if [ "$EUID" -ne 0 ]; then
    echo "Run with: sudo bash deploy/setup-ec2.sh"
    exit 1
fi

# Locate the directory containing this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing server dependencies..."
apt-get update
apt-get install -y python3 python3-venv python3-pip nginx rsync

echo "Creating Stat Lab directory..."
mkdir -p /home/ubuntu/stat-lab
chown ubuntu:ubuntu /home/ubuntu/stat-lab

echo "Configuring Nginx..."
cat > /etc/nginx/sites-available/stat-lab <<'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

ln -sfn /etc/nginx/sites-available/stat-lab /etc/nginx/sites-enabled/stat-lab
rm -f /etc/nginx/sites-enabled/default

nginx -t
systemctl enable nginx
systemctl restart nginx

echo "Installing Stat Lab service..."
cp "$SCRIPT_DIR/stat-lab.service" /etc/systemd/system/stat-lab.service
systemctl daemon-reload
systemctl enable stat-lab.service

echo "EC2 setup complete!"
echo "Next: deploy your application from your laptop."
