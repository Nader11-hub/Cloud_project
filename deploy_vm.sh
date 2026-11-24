#!/usr/bin/env bash
set -e

echo "=== [1/5] Updating packages and installing Nginx, Python3, and Pip ==="
sudo apt-get update -y
sudo apt-get install -y nginx python3 python3-pip python3-venv sqlite3 curl

echo "=== [2/5] Creating application directory ==="
sudo mkdir -p /var/www/login-monitor
sudo chown -R ubuntu:ubuntu /var/www/login-monitor

echo "=== [3/5] Setting up Python virtual environment ==="
cd /var/www/login-monitor
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install flask==3.0.3 werkzeug==3.0.3 gunicorn==22.0.0

echo "=== [4/5] Creating Systemd Service for Login Monitor ==="
sudo tee /etc/systemd/system/login-monitor.service > /dev/null << 'EOF'
[Unit]
Description=Login Monitor Gunicorn Service
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/login-monitor
Environment="PATH=/var/www/login-monitor/venv/bin"
Environment="DATA_DIR=/var/www/login-monitor/data"
ExecStart=/var/www/login-monitor/venv/bin/gunicorn --workers 2 --bind 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "=== [5/5] Configuring Nginx Reverse Proxy ==="
sudo tee /etc/nginx/sites-available/login-monitor > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/login-monitor /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

sudo systemctl daemon-reload
sudo systemctl enable login-monitor
sudo systemctl restart login-monitor
sudo systemctl restart nginx

echo "=== Deployment Completed Successfully! ==="
