#!/usr/bin/env python3
"""Enhanced local persist: store structured checks alongside the flat message."""
import os, json, datetime

env_path = "/c/Users/hello/alforaijboard-gh/.env"
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

timestamp = os.environ.get("RUN_AT", datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))

free_bytes = int(os.environ.get("FREE_MEM_KB", "0")) * 1024
total_bytes = int(os.environ.get("TOTAL_MEM_KB", "0")) * 1024
free_mb = free_bytes / (1024*1024)
total_mb = total_bytes / (1024*1024)

docker_running = os.environ.get("DOCKER_RUNNING","false") == "true"
docker_error = os.environ.get("DOCKER_ERROR","")[:500]

ram_pct = (free_mb / total_mb * 100) if total_mb else 0
ram_status = os.environ.get("RAM_STATUS","?")

disk_free_gb = float(os.environ.get("DISK_FREE_GB", 0) or 0)
disk_total_gb = float(os.environ.get("DISK_TOTAL_GB", 0) or 0)
disk_status = os.environ.get("DISK_STATUS","?")
disk_pct_free = (disk_free_gb / disk_total_gb * 100) if disk_total_gb else 0

git_changed = int(os.environ.get("GIT_CHANGED","0") or 0)
git_untracked = int(os.environ.get("GIT_UNTRACKED","0") or 0)
git_status = os.environ.get("GIT_STATUS","?")

agents_status = os.environ.get("AGENTS_STATUS","none-detected")

# Determine severities
def severity(status):
    return {"OK": "info", "WARNING": "warning", "CRITICAL": "critical"}.get(status, "unknown")

docker_sev = "info" if docker_running else "critical"
ram_sev = severity(ram_status)
disk_sev = severity(disk_status)
git_sev = "info" if git_status == "OK" else "warning"
agents_sev = "info" if agents_status and "0" not in agents_status.split()[0] else "warning"

# Overall
overall = "success"
if not docker_running or ram_status == "CRITICAL" or disk_status == "CRITICAL":
    overall = "warning"
if ram_status == "CRITICAL" or disk_status == "CRITICAL":
    overall = "critical"

# Flat message (for RLS fallback)
msg_parts = [
    f"Docker: {'RUNNING' if docker_running else 'DOWN'}",
    f"RAM: {round(free_mb,1)}MB free / {round(total_mb,1)}MB ({ram_status})",
    f"Disk C: {disk_free_gb:.1f}GB free / {disk_total_gb:.1f}GB ({disk_status})",
    f"Git: {git_changed} changed, {git_untracked} untracked ({git_status})",
    f"Agents: {agents_status}",
]
if docker_error:
    msg_parts.append(f"ERR: {docker_error}")

data = {
    "cron_id": f"cron_health_{timestamp.replace(':','-').replace('T','_')}",
    "host": os.environ.get("HOSTNAME", "DESKTOP-2U21BL4"),
    "timestamp": timestamp,
    "overall": overall,
    "checks": {
        "docker": {
            "status": "RUNNING" if docker_running else "DOWN",
            "severity": docker_sev,
            "details": "Docker Desktop daemon running." if docker_running else f"Failed: {docker_error}"
        },
        "ram": {
            "status": ram_status,
            "severity": ram_sev,
            "details": f"{round(free_mb,1)} MB free / {round(total_mb,1)} MB total ({ram_pct:.1f}%) — threshold: 500 MB"
        },
        "disk": {
            "status": disk_status,
            "severity": disk_sev,
            "details": f"{disk_free_gb:.1f} GB free / {disk_total_gb:.1f} GB total ({disk_pct_free:.1f}% free) — threshold: 10% free"
        },
        "git": {
            "status": git_status,
            "severity": git_sev,
            "details": f"{git_changed} changed files, {git_untracked} untracked — repo: alforaijboard-gh"
        },
        "agents": {
            "status": agents_status,
            "severity": agents_sev,
            "details": "Hermes agents / critical processes" if agents_status != "none-detected" else "No agent processes detected (may be idle)"
        }
    },
    # Flat message for external consumers
    "summary": " | ".join(msg_parts),
    "created_at": timestamp
}

path = "/c/Users/hello/alforaijboard-gh/cron_results_local.json"
rows = []
if os.path.exists(path):
    with open(path) as f:
        try:
            rows = json.load(f)
        except Exception:
            rows = []

rows.insert(0, data)
if len(rows) > 500:
    rows = rows[:500]

with open(path, "w") as f:
    json.dump(rows, f, indent=2)

print(f"Local persist: {path} — {len(rows)} rows (newest: {data['cron_id']})")
print(f"Overall: {overall}")
for name, check in data["checks"].items():
    print(f"  {name}: {check['status']} ({check['severity']}) — {check['details']}")
