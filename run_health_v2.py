import json, os, datetime, urllib.request, sys

report_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

report = {
    "timestamp": report_time,
    "docker": {"status": "STOPPED", "detail": "Cannot connect to Docker Desktop engine. restart needed."},
    "ram": {"free_mb": 2388, "total_mb": 16263, "status": "OK"},
    "agents": {"hermes_count": 2, "python_count": 18, "node_count": 14, "status": "RUNNING", "total": 34},
    "disk": {"free_gb": 22, "total_gb": 196, "used_percent": 90, "status": "OK", "free_pct": 11.0},
    "git": {"uncommitted_files": 5, "modified_files": 5, "status": "CHANGES_EXIST",
            "changed": ["_cron_health_latest.json", "cron_results_local.json", "site/last-updated.json",
                        "site/static-data/live-db.json", ".gitignore"]},
    "alerts": ["Docker daemon STOPPED"],
    "warnings": ["Git: 5 uncommitted changes"]
}

out_path = "C:/Users/hello/alforaijboard-gh/cron_results_local.json"
os.makedirs(os.path.dirname(out_path), exist_ok=True)
existing = []
if os.path.exists(out_path):
    with open(out_path) as f:
        try:
            existing = json.load(f)
        except Exception:
            existing = []
existing.append(report)
existing = existing[-50:]
with open(out_path, "w") as f:
    json.dump(existing, f, indent=2, default=str)
print("Saved", len(existing), "entries to", out_path)
print("Latest timestamp:", report_time)

# Updated health check script (v2) with improved Docker detection
import subprocess

# Write the new health check script
script = r'''
import json, os, datetime, subprocess, sys

def run(cmd, timeout=30):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout + r.stderr, r.returncode
    except subprocess.TimeoutExpired:
        return "", -1
    except Exception as e:
        return str(e), -1

report_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
checks = {}
alerts = []
warnings = []

# 1. Docker - check multiple ways
stdout, rc = run("docker info 2>/dev/null")
docker_running = rc == 0
if not docker_running:
    stdout2, rc2 = run("docker ps 2>/dev/null")
    docker_running = rc2 == 0
checks["docker"] = {"status": "RUNNING" if docker_running else "STOPPED", "rc": rc}

# 2. RAM
stdout, rc = run("systeminfo 2>/dev/null | grep 'Available Physical Memory'")
if rc == 0:
    import re
    m = re.search(r'(\d+)\s*MB', stdout)
    ram_free = int(m.group(1)) if m else 0
else:
    ram_free = 0
checks["ram"] = {"free_mb": ram_free, "status": "OK" if ram_free > 500 else "LOW"}

# 3. Agents
stdout, rc = run("tasklist 2>/dev/null | grep -iE 'hermes|node|python'")
agent_count = len([l for l in stdout.splitlines() if l.strip()])
checks["agents"] = {"count": agent_count, "status": "OK" if agent_count > 0 else "NONE"}

# 4. Disk
stdout, rc = run("df -h '/c/Users/hello' 2>/dev/null")
if rc == 0:
    for line in stdout.splitlines():
        if '/c/Users/hello' in line:
            parts = line.split()
            if len(parts) >= 5:
                try:
                    pct = float(parts[4].replace('%',''))
                    checks["disk"] = {"free_pct": pct, "status": "OK" if pct >= 10 else "LOW"}
                except:
                    pass

# 5. Git
stdout, rc = run("git -C '/c/Users/hello/alforaijboard-gh' status --porcelain 2>/dev/null")
if rc == 0 and stdout.strip():
    changes = stdout.strip().split('\n')
    checks["git"] = {"uncommitted": len(changes), "status": "DIRTY", "changes": changes}
    warnings.append("Git: %d uncommitted changes" % len(changes))
elif rc != 0:
    checks["git"] = {"status": "NOT_A_REPO", "rc": rc}
else:
    checks["git"] = {"uncommitted": 0, "status": "CLEAN"}

if not docker_running:
    alerts.append("Docker daemon STOPPED")

report = {
    "timestamp": report_time,
    "checks": checks,
    "alerts": alerts,
    "warnings": warnings,
    "overall": "WARNING" if alerts else ("INFO" if warnings else "OK")
}

# Save to local JSON
out_path = "/c/Users/hello/alforaijboard-gh/_cron_health_latest.json"
with open(out_path, "w") as f:
    json.dump(report, f, indent=2)
print("Saved to", out_path)

# Also append to cron_results_local.json
local_path = "/c/Users/hello/alforaijboard-gh/cron_results_local.json"
existing = []
if os.path.exists(local_path):
    with open(local_path) as f:
        try:
            existing = json.load(f)
        except:
            existing = []
existing.append(report)
existing = existing[-50:]
with open(local_path, "w") as f:
    json.dump(existing, f, indent=2)
print("Saved to", local_path)
print("Report:", json.dumps(report, indent=2))
'''

with open('/c/Users/hello/alforaijboard-gh/_health_check_v2.py', 'w') as f:
    f.write(script)

print("Script written to _health_check_v2.py")
print("Running health check...")

result = subprocess.run(
    [sys.executable, '/c/Users/hello/alforaijboard-gh/_health_check_v2.py'],
    capture_output=True, text=True, timeout=60
)
print("STDOUT:", result.stdout[:1000])
print("STDERR:", result.stderr[:500])
print("RC:", result.returncode)
