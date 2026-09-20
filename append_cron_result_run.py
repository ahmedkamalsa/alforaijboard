#!/usr/bin/env python3
"""Append this hour's health report to cron_results_local.json (Kuwait-time run)."""
import json, datetime, os, sys

results_path = "/c/Users/hello/alforaijboard-gh/cron_results_local.json"
now = datetime.datetime.now(datetime.timezone.utc)
ts = now.isoformat()
file_ts = now.strftime("%Y%m%d_%H%M")

# Live values from this run
new_entry = {
    "cron_id": f"cron_health_{file_ts}",
    "host": "DESKTOP-2U21BL4",
    "timestamp": ts,
    "overall": "NEEDS_ATTENTION",
    "checks": {
        "docker": {
            "status": "STOPPED",
            "severity": "error",
            "details": "Docker Desktop daemon not reachable — docker ps failed (npipe not found). Docker Desktop installed but not running."
        },
        "ram": {
            "status": "OK",
            "severity": "info",
            "details": "3460 MB free / 16263 MB total (21.3%) — threshold: 500 MB"
        },
        "hermes_agents": {
            "status": "OK",
            "severity": "info",
            "details": "8 processes: gateway (default) PIDs 15760/15836, gateway (alforaij-pro) PIDs 15640/15752, github MCP PIDs 20124/9528, playwright MCP PIDs 20140/11268 — all healthy"
        },
        "disk_c": {
            "status": "OK",
            "severity": "warning",
            "details": "20 GB free / 196 GB total (9.0% free) — BELOW 10% threshold, borderline"
        },
        "git_alforaijboard": {
            "status": "UNCOMMITTED_CHANGES",
            "severity": "warning",
            "details": "5 modified tracked files + 8 untracked files on alforaijboard repo: _cron_health_latest.json, append_cron_result.py, cron_results_local.json, site/last-updated.json, site/static-data/live-db.json modified; append_to_history.py, build_health_report.py, build_report.py, check_supabase_cron.py, cron_results_local.json.appender.py, print_latest.py, read_health.py, show_report.py untracked"
        }
    },
    "docker_status": "STOPPED",
    "ram_free_mb": 3460.0,
    "ram_total_mb": 16263.4,
    "disk_free_gb": 20.0,
    "disk_total_gb": 196.0,
    "disk_free_pct": 9.0,
    "hermes_agent_count": 8,
    "hermes_pids": "15760,15836,15640,15752,20124,9528,20140,11268",
    "git_modified": "_cron_health_latest.json,append_cron_result.py,cron_results_local.json,site/last-updated.json,site/static-data/live-db.json",
    "git_untracked_count": 8,
    "git_status": "UNCOMMITTED_CHANGES",
    "details": json.dumps({
        "docker": {"status": "STOPPED", "severity": "error", "details": "Docker Desktop not running — npipe:////./pipe/dockerDesktopLinuxEngine not found"},
        "ram": {"status": "OK", "severity": "info", "details": "3460 MB free / 16263 MB total (21.3%) — above 500 MB threshold"},
        "hermes_agents": {"status": "OK", "severity": "info", "details": "8 processes: gateway default x2 (PIDs 15760/15836) + gateway alforaij-pro x2 (PIDs 15640/15752) + github MCP x2 (PIDs 20124/9528) + playwright MCP x2 (PIDs 20140/11268)"},
        "disk_c": {"status": "OK", "severity": "warning", "details": "20 GB free / 196 GB total (9.0% free) — borderline below 10% threshold"},
        "git_alforaijboard": {"status": "UNCOMMITTED_CHANGES", "severity": "warning", "details": "5 modified tracked files + 8 untracked files — no push since last run"}
    }, ensure_ascii=False)
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

print(f"Appended {new_entry['cron_id']} — total entries now: {len(existing)}")
print(f"Latest: {ts} | OVERALL: NEEDS_ATTENTION")
print(f"  Docker: STOPPED (critical)")
print(f"  RAM: OK — 3460 MB free / 16263 MB total (21.3%)")
print(f"  Hermes agents: OK — 8 processes running")
print(f"  Disk C: WARN — 20 GB free (9.0%) — below 10% threshold")
print(f"  Git alforaijboard: UNCOMMITTED_CHANGES — 5 modified + 8 untracked files")
