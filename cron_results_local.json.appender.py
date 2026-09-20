#!/usr/bin/env python3
"""Append new cron result to cron_results_local.json (pure stdlib, no subprocess)."""
import json, datetime

results_path = "cron_results_local.json"

now = datetime.datetime.now(datetime.timezone.utc)
ts = now.isoformat()
file_ts = now.strftime("%Y%m%d_%H%M")

new_entry = {
    "cron_id": "cron_health_20260920_0350",
    "host": "DESKTOP-2U21BL4",
    "timestamp": "2026-09-20T03:50:44+00:00",
    "overall": "NEEDS_ATTENTION",
    "docker_status": "STOPPED",
    "ram_free_mb": 3217.7,
    "ram_total_mb": 16263.4,
    "disk_free_gb": 22.0,
    "disk_total_gb": 196.0,
    "disk_free_pct": 10.0,
    "processes_load_pct": 18,
    "git_modified": "",
    "git_untracked_count": 0,
    "git_status": "CLEAN",
    "checks": {
        "docker": {"status": "STOPPED", "severity": "error", "details": "Docker Desktop not running"},
        "ram": {"status": "OK", "severity": "info", "details": "3217.7 MB free / 16263.4 MB total (19.8%)"},
        "processes": {"status": "OK", "severity": "info", "details": "CPU load 18%, Hermes agents active"},
        "disk": {"status": "OK", "severity": "warning", "details": "22 GB free / 196 GB total (10.0% free) — edge of threshold"},
        "git": {"status": "CLEAN", "severity": "info", "details": "No uncommitted changes"}
    }
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

print(f"OK: {new_entry['cron_id']} appended — {len(existing)} total entries in {results_path}")
