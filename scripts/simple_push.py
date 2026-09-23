#!/usr/bin/env python3
"""Quick supabase push using local history data."""
import json, os, urllib.request
from pathlib import Path

SUPABASE_URL = "https://bwspcsiazbwrrxpgoldx.supabase.co"
SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

# Read from local history (last entry has current data)
hist_file = Path(r"C:\Users\hello\alforaijboard-gh\cron_results_local.json")
if not hist_file.exists():
    print("No cron_results_local.json")
    exit(1)

history = json.loads(hist_file.read_text())
last = history[-1] if history else {}
ts = last.get("timestamp", "")
cron_id = last.get("cron_id", "")

print(f"Latest entry: {cron_id} at {ts}")
print(f"Overall: {last.get('overall', '?')}")
print(f"Docker: {last.get('docker_status', '?')}")
print(f"RAM free: {last.get('ram_free_mb', '?')} MB")
print(f"Disk: {last.get('disk_free_pct', '?')}% free")
print(f"Git: {last.get('git_status', '?')}")
print(f"Hermes agents: {last.get('hermes_agent_count', '?')}")

if not SERVICE_KEY:
    print("\nNo SUPABASE_SERVICE_KEY env var.")
    print("Trying hardcoded key...")
    SERVICE_KEY = "sb_secret_dekuatGb5Z..."  # placeholder - user needs real key

if not SERVICE_KEY or len(SERVICE_KEY) < 20:
    print("\nCannot push to Supabase — no valid service key available.")
    print("To push, set SUPABASE_SERVICE_KEY env var or add it to the script.")
    exit(0)

row = {
    "timestamp": ts,
    "overall": last.get("overall", "UNKNOWN"),
    "docker_status": last.get("docker_status", ""),
    "ram_free_mb": last.get("ram_free_mb", 0),
    "ram_status": "OK",
    "disk_free_pct": last.get("disk_free_pct", 0),
    "disk_status": "OK" if last.get("disk_free_pct", 0) > 10 else "LOW",
    "git_status": last.get("git_status", ""),
    "details": json.dumps(last.get("details", {}), ensure_ascii=False),
    "name": cron_id,
    "status": "success" if last.get("overall", "") == "HEALTHY" else "error",
    "message": f"Health check {cron_id}: {last.get('overall', '')}",
}

API_URL = f"{SUPABASE_URL}/rest/v1/cron_results"
headers = {
    "Content-Type": "application/json",
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Prefer": "return=minimal",
}

print(f"\nPushing to {API_URL}...")
try:
    data_bytes = json.dumps(row).encode("utf-8")
    req = urllib.request.Request(API_URL, data=data_bytes, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = resp.read().decode()[:300]
        print(f"SUCCESS: HTTP {resp.status}")
        print(f"Body: {body}")
except Exception as e:
    print(f"FAILED: {e}")
