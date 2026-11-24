# Stage 2: Container Deployment & Volume Persistence Guide

This guide documents the execution, verification, and persistence testing for **Stage 2 (Containers)** of CET 322.

---

## 1. Components in Stage 2
* **Container Engine:** Docker Engine (v26+).
* **Base Image:** `python:3.12-slim` (minimal security attack surface).
* **Production Server:** Gunicorn WSGI with 2 worker processes.
* **Volume:** `cloud_project_db_volume` mounted at `/app/data` to ensure the SQLite database survives container crashes or restarts.
* **Network:** `cloud_project_network` (isolated bridge driver).

---

## 2. Execution Commands

### Step 1: Build the Docker Image
```bash
docker-compose build
# Or via raw docker CLI:
docker build -t login-monitor:latest .
```

### Step 2: Start the Container Stack
```bash
docker-compose up -d
```
The application will be live at:
👉 `http://localhost:5050`

*(Note: Port 5050 is intentionally used for Docker so that Stage 1 VM at port 8080 remains completely untouched and runnable concurrently!)*

---

## 3. Demonstration & TA Verification Steps (Checkpoint 1)

### Checkpoint Requirement 1: Service Opens in Host Browser
* Open `http://localhost:5050` in Firefox/Chrome.
* The SOC Dashboard is displayed with `Node Host` showing the container ID (e.g. `c5b7217d2fc3`).

### Checkpoint Requirement 2: Data Survives Restart (Persistence Test)
1. **Insert test logs into the running container:**
   ```bash
   curl -X POST -d "username=attacker&password=wrong" http://localhost:5050/login
   ```
2. **Restart the container:**
   ```bash
   docker restart login-monitor-app
   ```
3. **Verify data is still present:**
   ```bash
   curl -s http://localhost:5050/api/logs
   ```
   *Expected outcome:* The logs inserted prior to the restart are immediately returned. Data is intact because it resides in the named Docker volume `cloud_project_db_volume`.

---

## 4. Stopping the Container
```bash
docker-compose down
```
*(Data will still persist in the volume even after `docker-compose down` unless the `-v` flag is explicitly provided).*
