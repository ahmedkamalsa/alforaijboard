#!/usr/bin/env python3
"""Append this hour's health report to cron_results_local.json — using LIVE values from this run."""
import json, datetime, subprocess, os
from datetime import timezone, timedelta

results_path = "/c/Users/hello/alforaijboard-gh/cron_results_local.json"
tz = timezone(timedelta(hours=3))
now = datetime.datetime.now(tz)
ts = now.isoformat()
file_ts = now.strftime("%Y%m%d_%H%M")

# Collect live data from the health check script output we already have
# Re-run the health check to get fresh values
try:
    r = subprocess.run(
        ["cmd", "/c", "python", "C:/Users/hello/alforaijboard-gh/_health_check_now.py"],
        capture_output=True, text=True, timeout=30
    )
    live = json.loads(r.stdout)
except Exception as e:
    print(f"Failed to re-run health check: {e}")
    live = {"ram": {"status": "OK", "free_mb": 0, "total_gb": 0},
            "disk": {"status": "OK", "free_gb": 0, "total_gb": 0, "free_pct": 0},
            "docker": {"status": "DOWN", "error": "re-run failed"},
            "agents": {"status": "NONE", "count": 0, "procs": []},
            "git": {"status": "ERROR", "changes": []}}

ram = live.get("ram", {})
disk = live.get("disk", {})
docker = live.get("docker", {})
agents = live.get("agents", {})
git = live.get("git", {})

# Determine overall status
severities = []
for check in [docker, ram, disk, agents, git]:
    s = check.get("status", "ERROR")
    if s in ("DOWN", "LOW", "DIRTY", "ERROR", "NONE"):
        severities.append("error" if s in ("DOWN", "ERROR") else "warning")
    elif s == "OK":
        severities.append("info")

if "error" in severities:
    overall = "NEEDS_ATTENTION"
elif "warning" in severities:
    overall = "WARNING"
else:
    overall = "OK"

new_entry = {
    "cron_id": f"cron_health_{file_ts}",
    "host": "DESKTOP-2U21BL4",
    "timestamp": ts,
    "overall": overall,
    "checks": {
        "docker": {
            "status": docker.get("status", "DOWN"),
            "severity": "error" if docker.get("status") == "DOWN" else "info",
            "details": docker.get("error", "Docker Desktop daemon not reachable")[:200] if docker.get("status") == "DOWN" else "Docker Desktop daemon running."
        },
        "ram": {
            "status": ram.get("status", "OK"),
            "severity": "info",
            "details": f"{ram.get('free_mb', 0)} MB free / {ram.get('total_gb', 0)} GB total — threshold: 500 MB"
        },
        "disk": {
            "status": disk.get("status", "OK"),
            "severity": "warning" if disk.get("status") == "LOW" else "info",
            "details": f"{disk.get('free_gb', 0)} GB free / {disk.get('total_gb', 0)} GB total ({disk.get('free_pct', 0)}% free) — threshold: 10.0%"
        },
        "hermes_agents": {
            "status": agents.get("status", "NONE"),
            "severity": "info",
            "details": f"{agents.get('count', 0)} processes found" + (f": {agents.get('procs', [])[:3]}" if agents.get('count', 0) > 0 else " — NONE running")
        },
        "git": {
            "status": git.get("status", "ERROR"),
            "severity": "warning" if git.get("status") in ("DIRTY", "ERROR") else "info",
            "details": f"{len(git.get('changes', []))} changes: {git.get('changes', [])[:5]}" if git.get('status') in ("DIRTY", "ERROR") else "Clean"
        }
    },
    "docker_status": docker.get("status", "DOWN"),
    "ram_free_mb": float(ram.get("free_mb", 0)),
    "ram_total_mb": round(float(ram.get("total_gb", 0)) * 1024, 1),
    "disk_free_gb": float(disk.get("free_gb", 0)),
    "disk_total_gb": float(disk.get("total_gb", 0)),
    "disk_free_pct": float(disk.get("free_pct", 0)),
    "hermes_agent_count": int(agents.get("count", 0)),
    "hermes_pids": ",".join(str(p.get("pid", "")) for p in agents.get("procs", [])[:10]),
    "git_status": git.get("status", "ERROR"),
    "git_changes": git.get("changes", [])[:10],
}

try:
    with open(results_path) as f:
        existing = json.load(f)
except Exception:
    existing = []

if not any(e.get("cron_id") == new_entry["cron_id"] for e in existing):
    existing.append(new_entry)

with open(results_path, "w") as f:
    json.dump(existing, f, indent=2, ensure_ascii=False)

print(f"Appended {new_entry['cron_id']} — total entries: {len(existing)}, overall: {overall}")
