# Stage 1: Virtual Machine Deployment (Ubuntu Server + Nginx)

This guide documents the exact, repeatable steps to deploy the **Login Monitor Service** on an Ubuntu Virtual Machine behind an **Nginx Reverse Proxy**, fulfilling all requirements for **Stage 1 (Checkpoint 1)** of CET 322.

---

## 1. System Architecture & Components
* **Operating System:** Ubuntu Server 24.04 LTS (x86_64) on VirtualBox.
* **Component 1 (Web Application & API):** Python Flask app served using production-grade WSGI server (`gunicorn`).
* **Component 2 (Data Store):** SQLite relational database (`logins.db`).
* **Reverse Proxy:** Nginx listening on port 80 forwarding requests to `127.0.0.1:5000`.

---

## 2. Installation & Setup Steps

### Step 1: Update Packages & Install Dependencies
```bash
sudo apt-get update -y
sudo apt-get install -y nginx python3 python3-pip python3-venv sqlite3 curl
```

### Step 2: Create Application Directory
```bash
sudo mkdir -p /var/www/login-monitor
sudo chown -R ubuntu:ubuntu /var/www/login-monitor
cd /var/www/login-monitor
```

### Step 3: Python Virtual Environment & Requirements
```bash
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install flask==3.0.3 werkzeug==3.0.3 gunicorn==22.0.0
```

### Step 4: Configure Systemd Service
Create service file `/etc/systemd/system/login-monitor.service`:
```ini
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
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now login-monitor
```

### Step 5: Configure Nginx Reverse Proxy
Create `/etc/nginx/sites-available/login-monitor`:
```nginx
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
```

Enable site configuration and restart Nginx:
```bash
sudo ln -sf /etc/nginx/sites-available/login-monitor /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo systemctl restart nginx
```

---

## 3. Verification & Testing

### Test 1: From Host Browser
Open the following URL on your host browser (Parrot OS):
```
http://localhost:8080
```
You will see the **Login Monitor Dashboard** with:
* Real-time Login Form.
* Security Audit Table.
* Automated Brute-Force Alert Flagging (flags IPs with >= 3 failed logins).

### Test 2: CLI Healthcheck
```bash
curl -I http://localhost:8080
# Returns HTTP/1.1 200 OK via Server: nginx/1.24.0 (Ubuntu)
```
