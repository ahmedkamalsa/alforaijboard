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

# Try to read API key from .env file first
ENV_FILE = os.path.join(WORKDIR, ".env")
API_KEY = None
SERVICE_KEY = None

if os.path.exists(ENV_FILE):
    with open(ENV_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("SUPABASE_ANON_KEY="):
                API_KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
            elif line.startswith("SUPABASE_SERVICE_KEY="):
                SERVICE_KEY = line.split("=", 1)[1].strip().strip('"').strip("'")

# Fallback: read from environment
if not API_KEY:
    API_KEY = os.environ.get("SUPABASE_ANON_KEY")
if not SERVICE_KEY:
    SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

print(f"API key length: {len(API_KEY)} (first 10: {API_KEY[:10]}...)")
print(f"Service key length: {len(SERVICE_KEY)} (first 10: {SERVICE_KEY[:10] if SERVICE_KEY else 'None'}...)")

# Use service key for insert (bypasses RLS)
ACTIVE_KEY = SERVICE_KEY if SERVICE_KEY else API_KEY
if not ACTIVE_KEY:
    print("ERROR: No Supabase API key found (neither anon nor service).")
    print(f"  Tried env: SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY")
    print(f"  Tried file: {ENV_FILE}")
    sys.exit(1)

# Read the latest health report
REPORT_FILE = os.path.join(WORKDIR, "_cron_health_latest.json")
if not os.path.exists(REPORT_FILE):
    print(f"ERROR: Health report not found at {REPORT_FILE}")
    sys.exit(1)

with open(REPORT_FILE, "r") as f:
    raw = json.load(f)

# Normalize: the shell script writes timestamp/checks/summary,
# but older scripts used timestamp_utc/checks/alerts/all_ok.
# Accept both.
report = {}
report["timestamp"] = raw.get("timestamp") or raw.get("timestamp_utc", "")
report["checks"] = raw.get("checks", {})

if "summary" not in raw:
    parts = []
    for k in ["docker", "ram", "disk", "git"]:
        s = report["checks"].get(k, {}).get("status", "UNKNOWN")
        parts.append(s)
    report["summary"] = "|".join(parts)
else:
    report["summary"] = raw["summary"]

print("Health data keys:", list(report.keys()))
print("Checks keys:", list(report.get("checks", {}).keys()))

# Build the row to insert - only use columns that exist in the table
row = {
    "created_at": datetime.now(timezone.utc).isoformat(),
    "name": f"health_check_{datetime.now().strftime('%Y%m%d_%H%M')}",
    "status": "ok" if all(
        report["checks"].get(k, {}).get("status", "") in ("OK", "clean")
        for k in ["docker", "ram", "disk", "git"]
    ) else "error",
}

print("\nInsert payload:", json.dumps(row, indent=2))

# Build URL
url = f"https://{PROJECT_REF}.supabase.co/rest/v1/{TABLE_NAME}"
headers = {
    "Content-Type": "application/json",
    "apikey": ACTIVE_KEY,
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
