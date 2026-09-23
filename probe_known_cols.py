#!/usr/bin/env python3
"""Probe: push health report with known-good columns only (from GET row)."""
import os, json, urllib.request, urllib.error
PROJECT = "bwspcsiazbwrrxpgoldx"
URL = f"https://{PROJECT}.supabase.co"

# Keys from key_test3.py (embedded directly since .env missing)
ANON_KEY = "sb_publishable_c84oHQS94osRqw_SiTIqMg_8icxvatZ"

def push(row):
    headers = {
        "apikey": ANON_KEY,
        "Content-Type": "application/json",
    }
    body = json.dumps(row).encode("utf-8")
    req = urllib.request.Request(f"{URL}/rest/v1/cron_results", data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read().decode("utf-8", "replace")[:300]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")[:300]
    except Exception as e:
        return -1, repr(e)

# Known-good columns from successful GET row:
# id, name, status, message, duration_ms, records_affected, created_at
# Also observed: timestamp, overall, docker_status, ram_free_mb, ram_status,
#   disk_free_pct, disk_status, git_status, details
now = "2026-09-22T23:40:00+00:00"

print("=== Probe: known-good columns (minimal) ===", flush=True)
row_min = {
    "timestamp": now,
    "name": "probe_minimal",
    "status": "success",
    "message": "minimal known-columns probe",
    "duration_ms": 100,
    "records_affected": None,
}
code, msg = push(row_min)
print(f"  HTTP {code}: {msg}", flush=True)

print("\n=== Probe: full row with all observed columns ===", flush=True)
row_full = {
    "timestamp": now,
    "name": "probe_full",
    "status": "success",
    "message": "full observed-columns probe",
    "duration_ms": 100,
    "records_affected": None,
    "created_at": now,
    "overall": "HEALTHY",
    "docker_status": "RUNNING",
    "ram_free_mb": 5000,
    "ram_status": "OK",
    "disk_free_pct": 15.0,
    "disk_status": "OK",
    "git_status": "CLEAN",
    "details": json.dumps({"test": True}, ensure_ascii=False),
}
code, msg = push(row_full)
print(f"  HTTP {code}: {msg}", flush=True)

print("\n=== DONE ===", flush=True)
