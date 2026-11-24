# 🛡️ Cloud Security: Login Monitor

**CET 322 — Introduction to Cloud Computing | Track D: Cybersecurity**

A lightweight authentication monitoring and brute-force detection service built with Python (Flask), Gunicorn, SQLite, and Nginx, deployed across four cloud models: Virtual Machine, Containers, Kubernetes, and Hybrid.

## Features
- **Authentication Terminal:** Records every login attempt (username, IP address, user-agent, status, timestamp).
- **Brute-Force Detection:** Flags IP addresses with 3+ failed attempts within a 5-minute sliding window.
- **SOC Dashboard:** Live stats cards, status filters (`All` / `Failed` / `Success`), 30s auto-refresh, and admin actions (`Unblock IP`, `Clear All Logs`).
- **REST & Health Endpoints:** `/api/logs` and `/healthz`.

## Project Structure
- `app.py` — Flask application, SQLite integration, and SOC Dashboard UI.
- `requirements.txt` — Python dependencies.
- `deploy_vm.sh` — Automated Stage 1 deployment script for Ubuntu Server + Nginx + Gunicorn + Systemd.
- `STAGE1_GUIDE.md` — Repeatable Stage 1 setup and verification guide.

## Stage 1: Virtual Machine (Completed)
See [STAGE1_GUIDE.md](STAGE1_GUIDE.md) for full deployment instructions.
