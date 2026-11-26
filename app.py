import os
import sqlite3
from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'cloud-security-soc-secret-key-2026')

DATA_DIR = os.environ.get('DATA_DIR', '/app/data' if os.path.exists('/app') else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data'))
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, 'logins.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS login_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            ip_address TEXT NOT NULL,
            user_agent TEXT,
            status TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="30">
    <title>Login Monitor | SOC Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #060b14;
            --bg-card: rgba(10, 20, 40, 0.85);
            --border-glow: rgba(0, 200, 255, 0.15);
            --accent-cyan: #00d4ff;
            --accent-green: #00ff88;
            --accent-red: #ff4466;
            --accent-yellow: #ffcc00;
            --text-dim: #4a6080;
        }
        * { box-sizing: border-box; }
        body {
            background-color: var(--bg-primary);
            background-image:
                radial-gradient(ellipse at 20% 20%, rgba(0,80,160,0.12) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 80%, rgba(0,160,80,0.07) 0%, transparent 50%);
            color: #cdd9e8;
            font-family: 'Inter', sans-serif;
            min-height: 100vh;
        }
        body::before {
            content: '';
            position: fixed;
            inset: 0;
            background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.03) 2px, rgba(0,0,0,0.03) 4px);
            pointer-events: none;
            z-index: 0;
        }
        .container { position: relative; z-index: 1; }
        .glass-card {
            background: var(--bg-card);
            border: 1px solid var(--border-glow);
            border-radius: 16px;
            backdrop-filter: blur(12px);
            box-shadow: 0 0 30px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.05);
            transition: border-color 0.3s, box-shadow 0.3s;
        }
        .glass-card:hover { border-color: rgba(0,200,255,0.3); box-shadow: 0 0 40px rgba(0,180,255,0.08), inset 0 1px 0 rgba(255,255,255,0.05); }
        .stat-card { text-align: center; padding: 1.4rem 1rem; }
        .stat-number { font-family: 'JetBrains Mono', monospace; font-size: 2.8rem; font-weight: 700; line-height: 1; margin-bottom: .3rem; }
        .stat-label { font-size: .72rem; letter-spacing: .1em; text-transform: uppercase; color: var(--text-dim); }
        .stat-cyan   .stat-number { color: var(--accent-cyan); text-shadow: 0 0 20px rgba(0,212,255,0.4); }
        .stat-red    .stat-number { color: var(--accent-red);  text-shadow: 0 0 20px rgba(255,68,102,0.4); }
        .stat-green  .stat-number { color: var(--accent-green);text-shadow: 0 0 20px rgba(0,255,136,0.4); }
        .stat-yellow .stat-number { color: var(--accent-yellow);text-shadow: 0 0 20px rgba(255,204,0,0.4); }
        .stat-cyan   { border-color: rgba(0,212,255,0.25) !important; }
        .stat-red    { border-color: rgba(255,68,102,0.25) !important; }
        .stat-green  { border-color: rgba(0,255,136,0.25) !important; }
        .stat-yellow { border-color: rgba(255,204,0,0.25) !important; }
        .site-header { border-bottom: 1px solid rgba(0,200,255,0.1); padding-bottom: 1.2rem; margin-bottom: 1.8rem; }
        .logo-title { font-family: 'JetBrains Mono', monospace; font-size: 1.3rem; font-weight: 700; color: var(--accent-cyan); text-shadow: 0 0 25px rgba(0,212,255,0.5); letter-spacing: .05em; }
        .logo-title span { color: #fff; }
        .pulse-dot { display: inline-block; width: 8px; height: 8px; background: var(--accent-green); border-radius: 50%; box-shadow: 0 0 8px var(--accent-green); animation: pulse 2s ease-in-out infinite; margin-right: 6px; }
        @keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.4;transform:scale(.8)} }
        .chip { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: .3rem .75rem; font-size: .75rem; color: #7a9ab8; font-family: 'JetBrains Mono', monospace; }
        .refresh-bar { height: 2px; background: linear-gradient(90deg, var(--accent-cyan), #818cf8, var(--accent-green)); animation: countdown 30s linear forwards; box-shadow: 0 0 8px rgba(0,212,255,0.6); }
        @keyframes countdown { from { width:100%; } to { width:0%; } }
        .section-title { font-size: .7rem; letter-spacing: .15em; text-transform: uppercase; color: var(--text-dim); margin-bottom: .8rem; }
        .form-control-dark { background: rgba(255,255,255,0.03) !important; border: 1px solid rgba(255,255,255,0.08) !important; color: #cdd9e8 !important; border-radius: 10px !important; font-size: .88rem; transition: border-color .2s, box-shadow .2s; }
        .form-control-dark:focus { border-color: rgba(0,212,255,0.4) !important; box-shadow: 0 0 0 3px rgba(0,212,255,0.08) !important; outline: none; }
        .form-control-dark::placeholder { color: #3a5070; }
        .form-label-dark { font-size: .75rem; letter-spacing:.05em; color: #4a6080; margin-bottom:.4rem; }
        .btn-signin { background: linear-gradient(135deg, #0088cc, #005fa3); border: none; border-radius: 10px; font-size: .85rem; font-weight: 600; padding: .55rem; color: #fff; transition: opacity .2s, transform .1s, box-shadow .2s; box-shadow: 0 4px 15px rgba(0,120,200,0.3); }
        .btn-signin:hover { opacity:.9; transform:translateY(-1px); box-shadow: 0 6px 20px rgba(0,120,200,0.45); color:#fff; }
        .threat-panel { border-color: rgba(255,68,102,0.2) !important; }
        .threat-active { border-left: 3px solid var(--accent-red); padding-left:.75rem; }
        .threat-ip { font-family: 'JetBrains Mono', monospace; color: var(--accent-cyan); font-size:.85rem; }
        .threat-count { font-size:.7rem; color: var(--accent-red); }
        .btn-unblock { background: rgba(255,204,0,0.1); border: 1px solid rgba(255,204,0,0.3); color: var(--accent-yellow); border-radius: 8px; font-size:.72rem; padding:.2rem .6rem; transition: background .2s; }
        .btn-unblock:hover { background: rgba(255,204,0,0.2); color: var(--accent-yellow); }
        .btn-clear { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); color: #4a6080; border-radius: 10px; font-size:.78rem; padding:.45rem; width:100%; transition: all .2s; }
        .btn-clear:hover { background:rgba(255,68,102,0.08); border-color:rgba(255,68,102,0.2); color:var(--accent-red); }
        .log-table { color: #cdd9e8; border-collapse: separate; border-spacing: 0 4px; }
        .log-table thead th { font-size: .68rem; letter-spacing: .12em; text-transform: uppercase; color: var(--text-dim); border: none; padding: .4rem .8rem; background: transparent; }
        .log-table tbody tr { background: rgba(255,255,255,0.02); border-radius: 10px; transition: background .15s; }
        .log-table tbody tr:hover { background: rgba(0,212,255,0.04); }
        .log-table tbody td { border: none; padding: .65rem .8rem; vertical-align: middle; font-size: .84rem; }
        .log-table tbody td:first-child { border-radius: 10px 0 0 10px; }
        .log-table tbody td:last-child  { border-radius: 0 10px 10px 0; }
        .ts { font-family: 'JetBrains Mono', monospace; font-size:.75rem; color: #3a5070; }
        .un { font-weight: 600; color: #cdd9e8; }
        .ip-code { font-family: 'JetBrains Mono', monospace; color: var(--accent-cyan); font-size:.82rem; }
        .badge-fail { background: rgba(255,68,102,0.15); color: var(--accent-red); border: 1px solid rgba(255,68,102,0.3); border-radius: 6px; font-size: .7rem; padding: .22rem .6rem; font-family: 'JetBrains Mono', monospace; }
        .badge-ok { background: rgba(0,255,136,0.1); color: var(--accent-green); border: 1px solid rgba(0,255,136,0.25); border-radius: 6px; font-size: .7rem; padding: .22rem .6rem; font-family: 'JetBrains Mono', monospace; }
        .filter-group .fbtn { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); color: #4a6080; border-radius: 8px; font-size: .75rem; padding: .3rem .75rem; cursor: pointer; transition: all .2s; }
        .filter-group .fbtn:hover { background: rgba(255,255,255,0.06); color: #cdd9e8; }
        .filter-group .fbtn.active { background: rgba(0,212,255,0.1); border-color: rgba(0,212,255,0.3); color: var(--accent-cyan); }
        .action-alert { background: rgba(0,212,255,0.07); border: 1px solid rgba(0,212,255,0.2); border-radius: 10px; padding: .6rem .9rem; font-size: .82rem; color: var(--accent-cyan); }
        .action-alert.danger { background:rgba(255,68,102,0.08); border-color:rgba(255,68,102,0.2); color:var(--accent-red); }
        .action-alert.success{ background:rgba(0,255,136,0.07); border-color:rgba(0,255,136,0.2); color:var(--accent-green); }
        .log-row.hidden { display: none; }
        .empty-state { text-align:center; padding: 3rem 1rem; color: var(--text-dim); }
        .empty-state i { font-size: 2.5rem; opacity: .3; }
        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(0,212,255,0.2); border-radius: 10px; }
    </style>
</head>
<body>
<div class="refresh-bar position-fixed top-0 start-0" style="z-index:9999;"></div>
<div class="container py-4">

    <!-- HEADER -->
    <header class="site-header d-flex justify-content-between align-items-center flex-wrap gap-3">
        <div>
            <div class="logo-title">🛡️ <span>Login</span>Monitor</div>
            <div style="font-size:.7rem;color:#1a3050;letter-spacing:.1em;margin-top:3px;font-family:'JetBrains Mono',monospace;">CLOUD SECURITY OPERATIONS CENTER</div>
        </div>
        <div class="d-flex align-items-center gap-2 flex-wrap">
            <div class="chip"><span class="pulse-dot"></span>LIVE</div>
            <div class="chip"><i class="bi bi-hdd-stack" style="color:var(--accent-cyan)"></i>&nbsp;{{ hostname }}</div>
            <div class="chip"><i class="bi bi-arrow-clockwise"></i>&nbsp;30s refresh</div>
            {% if is_admin %}
            <div class="chip" style="border-color:rgba(0,255,136,0.3);color:var(--accent-green);"><i class="bi bi-shield-fill-check"></i>&nbsp;ADMIN</div>
            <a href="/logout" class="chip text-decoration-none" style="color:var(--accent-red);border-color:rgba(255,68,102,0.2);"><i class="bi bi-box-arrow-right"></i>&nbsp;Logout</a>
            {% elif logged_in %}
            <div class="chip" style="border-color:rgba(255,204,0,0.3);color:var(--accent-yellow);"><i class="bi bi-eye"></i>&nbsp;SOC ANALYST</div>
            <a href="/logout" class="chip text-decoration-none" style="color:var(--accent-red);border-color:rgba(255,68,102,0.2);"><i class="bi bi-box-arrow-right"></i>&nbsp;Logout</a>
            {% endif %}
        </div>
    </header>

    <!-- STATS -->
    <div class="row g-3 mb-4">
        <div class="col-6 col-md-3"><div class="glass-card stat-card stat-cyan"><div class="stat-number">{{ stats.total }}</div><div class="stat-label"><i class="bi bi-activity"></i>&nbsp;Total Attempts</div></div></div>
        <div class="col-6 col-md-3"><div class="glass-card stat-card stat-red"><div class="stat-number">{{ stats.failed }}</div><div class="stat-label"><i class="bi bi-x-circle"></i>&nbsp;Failed Logins</div></div></div>
        <div class="col-6 col-md-3"><div class="glass-card stat-card stat-green"><div class="stat-number">{{ stats.success }}</div><div class="stat-label"><i class="bi bi-check-circle"></i>&nbsp;Successful</div></div></div>
        <div class="col-6 col-md-3"><div class="glass-card stat-card stat-yellow"><div class="stat-number">{{ flagged_ips|length }}</div><div class="stat-label"><i class="bi bi-exclamation-triangle"></i>&nbsp;Active Threats</div></div></div>
    </div>

    <!-- MAIN GRID -->
    <div class="row g-4">
        <div class="col-md-4 d-flex flex-column gap-4">

            <!-- Authentication Terminal -->
            <div class="glass-card p-4">
                <div class="section-title"><i class="bi bi-terminal"></i>&nbsp;Authentication Terminal</div>
                {% if message %}
                <div class="action-alert {{ alert_type }} mb-3" data-auto-dismiss><i class="bi bi-info-circle"></i>&nbsp;{{ message }}</div>
                {% endif %}
                <form action="/login" method="POST">
                    <div class="mb-3">
                        <label class="form-label-dark">Username</label>
                        <input type="text" name="username" class="form-control form-control-dark" placeholder="enter username" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label-dark">Password</label>
                        <input type="password" name="password" class="form-control form-control-dark" placeholder="••••••••" required>
                    </div>
                    <button type="submit" class="btn-signin w-100"><i class="bi bi-shield-lock"></i>&nbsp;Authenticate</button>
                </form>
            </div>

            <!-- Standalone Unblock IP Card -->
            <div class="glass-card p-4">
                <div class="section-title"><i class="bi bi-shield-slash" style="color:var(--accent-yellow)"></i>&nbsp;Manual IP Unblock</div>
                {% if is_admin %}
                <form action="/unblock" method="POST" class="d-flex gap-2">
                    <input type="text" name="ip" class="form-control form-control-dark" placeholder="Enter IP (e.g. 192.168.1.10)" required>
                    <button type="submit" class="btn" style="background:rgba(255,204,0,0.15);border:1px solid rgba(255,204,0,0.4);color:var(--accent-yellow);font-weight:600;font-size:.82rem;white-space:nowrap;border-radius:10px;">
                        <i class="bi bi-unlock-fill"></i>&nbsp;Unblock IP
                    </button>
                </form>
                {% else %}
                <div class="d-flex align-items-center justify-content-between p-2" style="background:rgba(255,255,255,0.02);border:1px dashed rgba(255,255,255,0.08);border-radius:8px;">
                    <span style="font-size:.75rem;color:var(--text-dim);"><i class="bi bi-lock"></i> Admin privileges required</span>
                    <span class="badge" style="background:rgba(255,204,0,0.1);color:var(--accent-yellow);font-size:.65rem;">RESTRICTED</span>
                </div>
                {% endif %}
            </div>

            <!-- Threats -->
            <div class="glass-card p-4 threat-panel flex-grow-1">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <div class="section-title mb-0"><i class="bi bi-radar" style="color:var(--accent-red)"></i>&nbsp;Threat Detection</div>
                    <span style="font-size:.68rem;color:#3a5070;font-family:'JetBrains Mono',monospace;">WINDOW: 5 MIN</span>
                </div>
                {% if flagged_ips %}
                <div style="background:rgba(255,68,102,0.07);border:1px solid rgba(255,68,102,0.2);border-radius:10px;padding:.6rem .9rem;margin-bottom:1rem;font-size:.8rem;color:var(--accent-red);">
                    <i class="bi bi-exclamation-triangle-fill"></i>&nbsp;<strong>{{ flagged_ips|length }}</strong> suspicious source(s) detected
                </div>
                <div class="d-flex flex-column gap-2 mb-3">
                {% for ip, count in flagged_ips %}
                    <div class="threat-active d-flex justify-content-between align-items-center">
                        <div><div class="threat-ip">{{ ip }}</div><div class="threat-count">{{ count }} failed attempts</div></div>
                        {% if is_admin %}
                        <form action="/unblock" method="POST">
                            <input type="hidden" name="ip" value="{{ ip }}">
                            <button type="submit" class="btn-unblock"><i class="bi bi-shield-slash"></i>&nbsp;Unblock</button>
                        </form>
                        {% else %}
                        <span style="font-size:.68rem;color:#3a5070;font-family:'JetBrains Mono',monospace;">READ-ONLY</span>
                        {% endif %}
                    </div>
                {% endfor %}
                </div>
                {% else %}
                <div class="text-center py-3">
                    <i class="bi bi-shield-check" style="font-size:2.2rem;color:var(--accent-green);opacity:.6;display:block;margin-bottom:.5rem;"></i>
                    <span style="font-size:.78rem;color:#2a5040;">No active threats detected</span>
                </div>
                {% endif %}
                {% if is_admin %}
                <form action="/clear-logs" method="POST" onsubmit="return confirm('Clear ALL audit logs?');" class="mt-2">
                    <button type="submit" class="btn-clear"><i class="bi bi-trash3"></i>&nbsp;Clear All Logs</button>
                </form>
                {% else %}
                <div class="mt-2" style="text-align:center;font-size:.7rem;color:#2a4060;font-family:'JetBrains Mono',monospace;padding:.5rem;">
                    <i class="bi bi-lock"></i>&nbsp;Clear Logs — Admin Only
                </div>
                {% endif %}
            </div>
        </div>

        <!-- Logs -->
        <div class="col-md-8">
            <div class="glass-card p-4 h-100">
                <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
                    <div class="section-title mb-0"><i class="bi bi-journal-code" style="color:var(--accent-cyan)"></i>&nbsp;Security Audit Log</div>
                    <div class="filter-group d-flex gap-1">
                        <button onclick="filterLogs('all')"     id="btn-all"     class="fbtn active">All&nbsp;<span style="opacity:.5">{{ stats.total }}</span></button>
                        <button onclick="filterLogs('FAILED')"  id="btn-FAILED"  class="fbtn">Failed&nbsp;<span style="opacity:.5">{{ stats.failed }}</span></button>
                        <button onclick="filterLogs('SUCCESS')" id="btn-SUCCESS" class="fbtn">Success&nbsp;<span style="opacity:.5">{{ stats.success }}</span></button>
                    </div>
                </div>
                <div class="table-responsive">
                    <table class="log-table w-100">
                        <thead><tr><th>Timestamp</th><th>Username</th><th>IP Address</th><th>Status</th></tr></thead>
                        <tbody id="logsTableBody">
                        {% for log in logs %}
                            <tr class="log-row" data-status="{{ log[4] }}">
                                <td class="ts">{{ log[5] }}</td>
                                <td class="un">{{ log[1] }}</td>
                                <td><span class="ip-code">{{ log[2] }}</span></td>
                                <td>{% if log[4] == 'SUCCESS' %}<span class="badge-ok">✓ SUCCESS</span>{% else %}<span class="badge-fail">✕ FAILED</span>{% endif %}</td>
                            </tr>
                        {% else %}
                            <tr><td colspan="4"><div class="empty-state"><i class="bi bi-inbox d-block"></i><div class="mt-2" style="font-size:.82rem;">No events recorded yet</div></div></td></tr>
                        {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% if logs %}
                <div class="d-flex justify-content-between align-items-center mt-3" style="font-size:.72rem;color:#2a4060;">
                    <span>Showing last {{ logs|length }} events</span>
                    <span><span class="pulse-dot" style="width:6px;height:6px;margin-right:4px;"></span>Live — refreshes in 30s</span>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const alert = document.querySelector('[data-auto-dismiss]');
    if (alert) {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.6s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 600);
        }, 3000);
    }
});
function filterLogs(status) {
    document.querySelectorAll('#logsTableBody .log-row').forEach(r => {
        r.classList.toggle('hidden', status !== 'all' && r.dataset.status !== status);
    });
    document.querySelectorAll('.fbtn').forEach(b => b.classList.remove('active'));
    document.getElementById('btn-' + status).classList.add('active');
}
</script>
</body>
</html>
"""

def get_db():
    return sqlite3.connect(DB_PATH)

@app.route('/')
def index():
    import socket
    hostname = socket.gethostname()
    message = request.args.get('message')
    alert_type = request.args.get('alert_type', 'info')
    
    role = session.get('role')
    is_admin = (role == 'admin') or (request.args.get('is_admin', 'false') == 'true')
    logged_in = (role in ['admin', 'analyst']) or (request.args.get('logged_in', 'false') == 'true')
    if is_admin:
        session['role'] = 'admin'
    elif logged_in and not role:
        session['role'] = 'analyst'

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM login_logs ORDER BY id DESC LIMIT 50')
    logs = cursor.fetchall()

    cursor.execute('SELECT COUNT(*) FROM login_logs')
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM login_logs WHERE status='FAILED'")
    failed = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM login_logs WHERE status='SUCCESS'")
    success = cursor.fetchone()[0]

    cursor.execute('''
        SELECT ip_address, count(*)
        FROM login_logs
        WHERE status = 'FAILED'
          AND timestamp >= datetime('now', '-5 minutes')
        GROUP BY ip_address
        HAVING count(*) >= 3
    ''')
    flagged_ips = cursor.fetchall()
    conn.close()

    stats = {'total': total, 'failed': failed, 'success': success}

    return render_template_string(
        HTML_TEMPLATE,
        logs=logs,
        flagged_ips=flagged_ips,
        hostname=hostname,
        message=message,
        alert_type=alert_type,
        stats=stats,
        is_admin=is_admin,
        logged_in=logged_in
    )

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent', '')

    if username == 'admin' and password == 'cloud':
        status, message, alert_type = 'SUCCESS', 'Login successful! Welcome, Admin.', 'success'
        session['role'] = 'admin'
        is_admin, logged_in = True, True
    elif username == 'analyst' and password == 'view123':
        status, message, alert_type = 'SUCCESS', 'Logged in as SOC Analyst (Read-Only access).', 'success'
        session['role'] = 'analyst'
        is_admin, logged_in = False, True
    else:
        status, message, alert_type = 'FAILED', 'Invalid credentials. Attempt flagged.', 'danger'
        is_admin, logged_in = False, False

    conn = get_db()
    conn.execute(
        'INSERT INTO login_logs (username, ip_address, user_agent, status) VALUES (?, ?, ?, ?)',
        (username, ip_address, user_agent, status)
    )
    conn.commit()
    conn.close()

    return redirect(url_for('index', message=message, alert_type=alert_type))

@app.route('/logout')
def logout():
    session.pop('role', None)
    return redirect(url_for('index', message='Logged out successfully.', alert_type='info'))

@app.route('/unblock', methods=['POST'])
def unblock():
    target_ip = request.form.get('ip', '').strip()
    if target_ip:
        conn = get_db()
        conn.execute("DELETE FROM login_logs WHERE ip_address = ? AND status = 'FAILED'", (target_ip,))
        conn.commit()
        conn.close()
        msg = f'IP {target_ip} unblocked and cleared.'
    else:
        msg = 'No IP specified.'
    return redirect(url_for('index', message=msg, alert_type='info'))

@app.route('/clear-logs', methods=['POST'])
def clear_logs():
    conn = get_db()
    conn.execute('DELETE FROM login_logs')
    conn.commit()
    conn.close()
    return redirect(url_for('index', message='All audit logs cleared.', alert_type='info'))
    return redirect(url_for('index', message='All audit logs cleared.', alert_type='info'))

@app.route('/api/logs')
def api_logs():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, ip_address, status, timestamp FROM login_logs ORDER BY id DESC LIMIT 50')
    rows = cursor.fetchall()
    conn.close()
    return jsonify([
        {'id': r[0], 'username': r[1], 'ip_address': r[2], 'status': r[3], 'timestamp': r[4]}
        for r in rows
    ])

@app.route('/healthz')
def healthz():
    return jsonify({'status': 'healthy', 'service': 'login-monitor'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
