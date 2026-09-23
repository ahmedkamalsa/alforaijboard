#!/usr/bin/env python3
"""Probe Supabase schema and push a minimal health row"""
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

PROJECT_REF = "bwspcsiazbwrrxpgoldx"

# Read API key
KEY_FILE = "/c/Users/hello/alforaijboard-gh/supabase_data/supabase_key.txt"
API_KEY = None
if os.path.exists(KEY_FILE):
    with open(KEY_FILE) as f:
        API_KEY = f.read().strip()
if not API_KEY:
    API_KEY = os.environ.get("SUPABASE_ANON_KEY") or os.environ.get("SUPABASE_SERVICE_KEY")
if not API_KEY:
    print("ERROR: No API key")
    sys.exit(1)

print(f"API key length: {len(API_KEY)} (first 10: {API_KEY[:10]}...)")

# 1) Check schema for cron_results table columns
print("\n=== Checking schema for cron_results ===")
schema_url = f"https://{PROJECT_REF}.supabase.co/rest/v1/"
schema_headers = {"apikey": API_KEY, "Content-Type": "application/json"}
try:
    with urllib.request.urlopen(urllib.request.Request(schema_url, headers=schema_headers), timeout=15) as resp:
        print(f"Schema endpoint HTTP {resp.status}")
        body = resp.read().decode("utf-8", errors="replace")
        print(f"Response ({len(body)} bytes): {body[:500]}")
except Exception as e:
    print(f"Schema check failed: {e}")

# 2) Try to insert with only guaranteed columns
print("\n=== Trying minimal insert ===")
minimal_row = {
    "created_at": datetime.now(timezone.utc).isoformat(),
    "status": "error",
    "docker_status": "DOWN",
    "docker_msg": "Docker daemon not running",
    "ram_status": "OK",
    "ram_free_mb": 3108,
    "ram_msg": "3108MB free",
    "agents_status": "OK",
    "agents_count": 0,
    "agents_procs": "",
    "disk_status": "OK",
    "disk_free": "22G",
    "disk_use_pct": 89,
    "disk_msg": "22GB free (89% used)",
    "git_status": "DIRTY",
    "git_dirty_count": 59,
    "git_msg": "Git repo has 59 uncommitted changes",
    "summary": "DOWN|OK|OK|DIRTY",
    "alerts": 2,
    "timestamp": datetime.now().strftime("%Y%m%d_%H%M"),
}

print("Insert payload:", json.dumps(minimal_row, indent=2))

insert_url = f"https://{PROJECT_REF}.supabase.co/rest/v1/cron_results"
insert_headers = {
    "Content-Type": "application/json",
    "apikey": API_KEY,
    "Prefer": "return=minimal",
}
data = json.dumps(minimal_row).encode("utf-8")
req = urllib.request.Request(insert_url, data=data, headers=insert_headers, method="POST")

try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read().decode("utf-8")
        print(f"\nInsert HTTP {resp.status}: {body}")
        if resp.status == 201:
            print("\n✓ Insert succeeded!")
except urllib.error.HTTPError as e:
    print(f"\nInsert HTTP Error {e.code}: {e.reason}")
    print(e.read().decode("utf-8", errors="replace"))
    sys.exit(1)
except urllib.error.URLError as e:
    print(f"\nInsert URL Error: {e.reason}")
    sys.exit(1)
