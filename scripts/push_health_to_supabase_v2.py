#!/usr/bin/env python3
"""
Push health check result to Supabase cron_results table.
Uses native Windows Python (no pip install needed - uses stdlib urllib).
README: https://supabase.com/docs/guides/api/rest/insert
"""
import os
import sys
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone

WORKDIR = "/c/Users/hello/alforaijboard-gh"

# Config - adjust PROJECT_REF and API KEY as needed
PROJECT_REF = "bwspcsiazbwrrxpgoldx"  # your Supabase project
TABLE_NAME = "cron_results"

# Try to read API key from file first (common pattern in this project)
KEY_FILE = os.path.join(WORKDIR, ".env")  # Supabase keys typically in .env
ALTERNATE_KEY_FILE = os.path.join(WORKDIR, "supabase_data", "supabase_key.txt")
API_KEY = None

if os.path.exists(KEY_FILE):
    with open(KEY_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("SUPABASE_ANON_KEY="):
                API_KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
                break
            elif line.startswith("SUPABASE_SERVICE_KEY="):
                API_KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
                break

# Fallback: try alternate key file
if not API_KEY and os.path.exists(ALTERNATE_KEY_FILE):
    with open(ALTERNATE_KEY_FILE, "r") as f:
        API_KEY = f.read().strip()

# Fallback: read from environment
if not API_KEY:
    API_KEY = os.environ.get("SUPABASE_ANON_KEY") or os.environ.get("SUPABASE_SERVICE_KEY")

if not API_KEY:
    print("ERROR: No Supabase API key found.")
    print(f"  Tried: {ENV_FILE}")
    print("  Tried env vars: SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY")
    print("  Get your anon key from: https://supabase.com/dashboard/project/" + PROJECT_REF + "/settings/api")
    sys.exit(1)

print(f"API key length: {len(API_KEY)} (first 10: {API_KEY[:10]}...)")

# Read the latest health report
REPORT_FILE = os.path.join(WORKDIR, "_cron_health_latest.json")
if not os.path.exists(REPORT_FILE):
    print(f"ERROR: Health report not found at {REPORT_FILE}")
    sys.exit(1)

with open(REPORT_FILE, "r") as f:
    health_data = json.load(f)

# Normalize: the shell script writes timestamp/checks/summary,
# but older scripts used timestamp_utc/checks/alerts/all_ok.
# Accept both.
if "timestamp" not in health_data:
    health_data["timestamp"] = health_data.get("timestamp_utc", "")
if "summary" not in health_data:
    parts = []
    for k in ["docker", "ram", "disk", "git"]:
        s = health_data["checks"].get(k, {}).get("status", "UNKNOWN")
        parts.append(s)
    health_data["summary"] = "|".join(parts)

print("Health data keys:", list(health_data.keys()))
print("Checks keys:", list(health_data.get("checks", {}).keys()))

# Build the row to insert - only use columns that exist in the table
# Based on earlier probe, the table has these columns:
# created_at, status, docker_status, docker_msg, ram_status, ram_free_mb, ram_msg,
# agents_status, agents_count, agents_procs, disk_status, disk_free, disk_use_pct, disk_msg,
# git_status, git_dirty_count, git_msg, summary, alerts, timestamp

row = {
    "created_at": datetime.now(timezone.utc).isoformat(),
    "timestamp": health_data.get("timestamp", datetime.now().strftime("%Y%m%d_%H%M")),
    "docker_status": health_data["checks"]["docker"].get("status", "UNKNOWN"),
    "docker_msg": health_data["checks"]["docker"].get("msg", ""),
    "ram_status": health_data["checks"]["ram"].get("status", "UNKNOWN"),
    "ram_free_mb": health_data["checks"]["ram"].get("free_mb", 0),
    "ram_msg": health_data["checks"]["ram"].get("msg", ""),
    "agents_status": health_data["checks"]["agents"].get("status", "UNKNOWN"),
    "agents_count": health_data["checks"]["agents"].get("count", 0),
    "agents_procs": health_data["checks"]["agents"].get("procs", ""),
    "disk_status": health_data["checks"]["disk"].get("status", "UNKNOWN"),
    "disk_free": health_data["checks"]["disk"].get("free", ""),
    "disk_use_pct": health_data["checks"]["disk"].get("use_pct", 0),
    "disk_msg": health_data["checks"]["disk"].get("msg", ""),
    "git_status": health_data["checks"]["git"].get("status", "UNKNOWN"),
    "git_dirty_count": health_data["checks"]["git"].get("dirty_count", 0),
    "git_msg": health_data["checks"]["git"].get("msg", ""),
    "summary": health_data.get("summary", ""),
    "status": "ok" if all(
        health_data["checks"][k].get("status", "") in ("OK", "clean")
        for k in ["docker", "ram", "disk", "git"]
    ) else "error",
    "alerts": sum(
        1 for k in ["docker", "ram", "disk", "git"]
        if health_data["checks"][k].get("status", "") not in ("OK", "clean")
    )
}

print("\nInsert payload:", json.dumps(row, indent=2))

# Build URL
url = f"https://{PROJECT_REF}.supabase.co/rest/v1/{TABLE_NAME}"
headers = {
    "Content-Type": "application/json",
    "apikey": API_KEY,
    "Prefer": "return=minimal",
}

data = json.dumps(row).encode("utf-8")
req = urllib.request.Request(url, data=data, headers=headers, method="POST")

try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read().decode("utf-8")
        status_code = resp.status
        print(f"\nResponse ({status_code}): {body}")
        if status_code == 201:
            print("\nSUCCESS: Health check result saved to Supabase!")
        else:
            print(f"\nWARNING: Unexpected status code {status_code}")
except urllib.error.HTTPError as e:
    print(f"\nHTTP Error {e.code}: {e.reason}")
    print(f"Response: {e.read().decode('utf-8', errors='replace')}")
    # If PGRST204, the column doesn't exist - try without it
    if e.code == 400 and "Could not find" in e.read().decode('utf-8', errors='replace'):
        print("\nColumn not found - trying without problematic fields...")
        # Try again with only known-good columns
        retry_row = {k: v for k, v in row.items() if k not in ("agents_count", "agents_procs")}
        retry_data = json.dumps(retry_row).encode("utf-8")
        retry_req = urllib.request.Request(url, data=retry_data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(retry_req, timeout=30) as retry_resp:
                retry_body = retry_resp.read().decode("utf-8")
                print(f"Retry response ({retry_resp.status}): {retry_body}")
                if retry_resp.status == 201:
                    print("\nSUCCESS on retry!")
        except Exception as retry_e:
            print(f"Retry failed: {retry_e}")
    sys.exit(1)
except urllib.error.URLError as e:
    print(f"\nURL Error: {e.reason}")
    print("Check your internet connection and Supabase project URL.")
    sys.exit(1)
