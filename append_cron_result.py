#!/usr/bin/env python3
"""Append new cron result to cron_results_local.json (no subprocess, pure stdlib)."""
import json, datetime

results_path = "/c/Users/hello/alforaijboard-gh/cron_results_local.json"

new_entry = {
    "cron_id": "cron_health_20260919_2251",
    "host": "DESKTOP-2U21BL4",
    "timestamp": "2026-09-19T22:51:00+00:00",
    "overall": "NEEDS_ATTENTION",
    "checks": {
        "docker": {
            "status": "STOPPED",
            "severity": "error",
            "details": "Docker Desktop daemon not reachable - docker ps failed with connection error"
        },
        "ram": {
            "status": "OK",
            "severity": "info",
            "details": "5907.2 MB free / 16263.4 MB total (36.3%) - threshold: 500 MB"
        },
        "processes": {
            "status": "OK",
            "severity": "info",
            "details": "CPU load 42% - cron job runs in isolated shell, Hermes agents are separate processes"
        },
        "disk": {
            "status": "OK",
            "severity": "warning",
            "details": "22 GB free / 196 GB total (10.0% free) - threshold: 10.0% - right at the edge"
        },
        "git": {
            "status": "DIRTY",
            "severity": "warning",
            "details": "Modified: site/last-updated.json, site/static-data/live-db.json. Untracked: 4 files"
        }
    },
    "docker_status": "STOPPED",
    "ram_free_mb": 5907.2,
    "ram_total_mb": 16263.4,
    "disk_free_gb": 22.0,
    "disk_total_gb": 196.0,
    "disk_free_pct": 10.0,
    "processes_load_pct": 42,
    "git_modified": "site/last-updated.json, site/static-data/live-db.json",
    "git_untracked_count": 4,
    "git_status": "DIRTY",
    "details": "{\"docker\":{\"status\":\"STOPPED\",\"severity\":\"error\",\"details\":\"Docker Desktop daemon not reachable\"},\"ram\":{\"status\":\"OK\",\"severity\":\"info\",\"details\":\"5907.2 MB free / 16263.4 MB total (36.3%)\"},\"processes\":{\"status\":\"OK\",\"severity\":\"info\",\"details\":\"CPU load 42%\"},\"disk\":{\"status\":\"OK\",\"severity\":\"warning\",\"details\":\"22 GB free / 196 GB total (10.0% free)\"},\"git\":{\"status\":\"DIRTY\",\"severity\":\"warning\",\"details\":\"Modified: site/last-updated.json, site/static-data/live-db.json. Untracked: 4 files\"}}"
}

try:
    with open(results_path) as f:
        existing = json.load(f)
except Exception:
    existing = []

# avoid duplicates by cron_id
if not any(e.get("cron_id") == new_entry["cron_id"] for e in existing):
    existing.append(new_entry)

with open(results_path, "w") as f:
    json.dump(existing, f, indent=2, ensure_ascii=False)

print(f"Appended {new_entry['cron_id']} — total entries: {len(existing)}")
