# Project Proposal (D1)
**Course:** CET 322 — Introduction to Cloud Computing  
**Project Title:** One Service, Four Ways: Login Monitor & Brute-Force Detection System  
**Track:** Track D: Cybersecurity  
**Academic Year:** 2026/2027  
**Submission Date:** Week 9 Checkpoint  

---

## 1. Problem Statement & Target Users
* **Problem:** Web applications and cloud services face persistent automated credential stuffing and brute-force attacks. System administrators and Security Operations Center (SOC) teams require real-time visibility into authentication attempts to identify and mitigate hostile IP sources before security breaches occur.
* **Target Users:** Cloud System Administrators, SOC Analysts, and DevOps/SecOps engineers seeking a lightweight, observable authentication monitoring layer.
* **Service Goal:** Provide an observable authentication gateway that logs all login attempts, automatically detects repeated authentication failures (>= 3 failures within a 5-minute sliding window), and provides administrative controls (unblock/clear logs) alongside actionable metrics.

---

## 2. System Components (Two-Component Model)
The service adheres strictly to the required two-component architecture:

1. **Component 1 (Web Application & API):**
   * Built with **Python (Flask)** served via production WSGI server (**Gunicorn**).
   * Implements the authentication endpoint (`/login`), live SOC Dashboard UI, and REST endpoints (`/api/logs` and `/healthz`).
   * Evaluates authentication thresholds and tags hostile IP addresses in real time.
2. **Component 2 (Data Store):**
   * **SQLite Database** (`logins.db`) storing structured audit logs: `(id, username, ip_address, user_agent, status, timestamp)`.
   * Designed to support persistent volume mounting across Docker, Kubernetes, and Hybrid deployments.

---

## 3. Team Roles and Responsibilities
*(Team size: 5–8 members as defined in Section 6, Table 4)*

| Role | Team Member Name | Primary Responsibility |
|---|---|---|
| **Team Lead** | *[Insert Name - e.g., Nader]* | Project planning, weekly syncs, Git repository management, TA coordination. |
| **Application Developer** | *[Insert Name]* | Application logic (`app.py`), database schema, threat detection window. |
| **VM Engineer** | *[Insert Name]* | Stage 1 VM setup, Nginx reverse proxy configuration, and Stage 4 DB VM. |
| **Container Engineer** | *[Insert Name]* | Stage 2 containerization, Dockerfile, Docker networks, and volume persistence. |
| **Kubernetes Engineer** | *[Insert Name]* | Stage 3 Minikube cluster deployment, ReplicaSets, self-healing, and Services. |
| **Integration & Measurement Lead** | *[Insert Name]* | Stage 4 hybrid integration and metric benchmarks (Table 7). |
| **Documentation & Demo Lead** | *[Insert Name]* | Technical report, architectural diagrams, README, and backup video (D6). |

---

## 4. Architectural Overview (The Four Deployments)

```
[ Stage 1: Virtual Machine ]
Host Browser (localhost:8080) ──> [ VirtualBox VM (Ubuntu Server) ]
                                    ├── Nginx (Port 80) ── Reverse Proxy ──> Gunicorn:5000 (app.py)
                                    └── Data Store: SQLite (Local Disk)

[ Stage 2: Containers ]
Client Request ──> Docker Bridge Network
                    ├── Container 1: Web App (Gunicorn/Flask)
                    └── Container 2 / Volume: Persistent Database Storage

[ Stage 3: Kubernetes ]
Client Traffic ──> K8s Service (NodePort/ClusterIP)
                    └── K8s Deployment (2 Replicas, Auto-healing & Scaling to 4)

[ Stage 4: Hybrid Architecture ]
Client ──> K8s Cluster (Web App Deployment in Containers)
              └── Network Connection (IP Address) ──> Dedicated Ubuntu VM (Isolated Database)
```

---

## 5. Expected Milestones
* **Week 9:** Proposal submission and approval (Checkpoint D1).
* **Week 10:** Stage 1 (VM + Nginx) and Stage 2 (Docker Container & Volume) completion.
* **Week 11:** Stage 3 (Kubernetes Deployment, 2 replicas, self-healing demonstration).
* **Week 12:** Stage 4 (Hybrid integration) and comparison measurements (Table 7).
* **Week 13:** Technical report submission, backup video recording, and final presentation.
