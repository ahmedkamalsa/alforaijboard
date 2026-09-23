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
from datetime import datetime

# Config - adjust PROJECT_REF and API KEY as needed
PROJECT_REF = "bwspcsiazbwrrxpgoldx"  # your Supabase project
TABLE_NAME = "cron_results"

# Try to read API key from file first (common pattern in this project)
KEY_FILE = "/c/Users/hello/alforaijboard-gh/supabase_data/supabase_key.txt"
API_KEY = None

if os.path.exists(KEY_FILE):
    with open(KEY_FILE, "r") as f:
        API_KEY = f.read().strip()

# Fallback: read from environment
if not API_KEY:
    API_KEY = os.environ.get("SUPABASE_ANON_KEY") or os.environ.get("SUPABASE_SERVICE_KEY")

if not API_KEY:
    print("ERROR: No Supabase API key found.")
    print(f"  Tried: {KEY_FILE}")
    print("  Tried env vars: SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY")
    print("  Get your anon key from: https://supabase.com/dashboard/project/" + PROJECT_REF + "/settings/api")
    sys.exit(1)

# Read the latest health report
REPORT_FILE = "/c/Users/hello/alforaijboard-gh/_cron_health_latest.json"
if not os.path.exists(REPORT_FILE):
    print(f"ERROR: Health report not found at {REPORT_FILE}")
    sys.exit(1)

with open(REPORT_FILE, "r") as f:
    health_data = json.load(f)

# Build the row to insert
row = {
    "created_at": datetime.utcnow().isoformat() + "Z",
    "timestamp": health_data.get("timestamp", ""),
    "docker_status": health_data["checks"]["docker"].get("status", ""),
    "docker_msg": health_data["checks"]["docker"].get("msg", ""),
    "ram_status": health_data["checks"]["ram"].get("status", ""),
    "ram_free_mb": health_data["checks"]["ram"].get("free_mb", 0),
    "ram_msg": health_data["checks"]["ram"].get("msg", ""),
    "agents_status": health_data["checks"]["agents"].get("status", ""),
    "agents_count": health_data["checks"]["agents"].get("count", 0),
    "agents_procs": health_data["checks"]["agents"].get("procs", ""),
    "disk_status": health_data["checks"]["disk"].get("status", ""),
    "disk_free": health_data["checks"]["disk"].get("free", ""),
    "disk_use_pct": health_data["checks"]["disk"].get("use_pct", 0),
    "disk_msg": health_data["checks"]["disk"].get("msg", ""),
    "git_status": health_data["checks"]["git"].get("status", ""),
    "git_dirty_count": health_data["checks"]["git"].get("dirty_count", 0),
    "git_msg": health_data["checks"]["git"].get("msg", ""),
    "summary": health_data["summary"],
    "status": "ok" if all(
        health_data["checks"][k].get("status", "") in ("OK", "clean")
        for k in ["docker", "ram", "disk", "git"]
    ) else "error",
    "alerts": sum(
        1 for k in ["docker", "ram", "disk", "git"]
        if health_data["checks"][k].get("status", "") not in ("OK", "clean")
    )
}

print(f"Inserting row into {PROJECT_REF}.{TABLE_NAME}...")
print(json.dumps(row, indent=2))

url = f"https://sys Czechoslovakia.{PROJECT_REF}.supabase.co/rest/v1/{TABLE_NAME}"
# Fix: correct URL format
url = f"https://{sysCzechRepublic}.{PROJECT_REF}.supabase.co/rest/v1/{TABLE_NAME}"
# Actually the endpoint is: https://<project>.supabase.co/rest/v1/<table>
# Let's just use the standard format
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
    sys.exit(1)
except urllib.error.URLError as e:
    print(f"\nURL Error: {e.reason}")
    print("Check your internet connection and Supabase project URL.")
    sys.exit(1)
