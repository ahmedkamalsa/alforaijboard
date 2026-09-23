#!/usr/bin/env python3
import json, os, urllib.request
from pathlib import Path

SUPABASE_URL = "https://bwspcsiazbwrrxpgoldx.supabase.co"
SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

results_file = Path(r"C:\Users\hello\alforaijboard-gh\scripts\_cron_health_latest.json")
if not results_file.exists():
    print("No results file found")
    exit(1)

data = json.loads(results_file.read_text())
ts = data.get("timestamp", "")
file_ts = data.get("file_ts", "")
checks = data.get("checks", {})
overall = data.get("overall", "UNKNOWN")

print(f"Pushing health report: {file_ts}")

# Rebuild report_text from checks for the message field
report_lines = [f"=== SYSTEM HEALTH REPORT — {ts} ==="]
for name, c in checks.items():
    status = c.get("status", "?")
    details = c.get("details", "")
    report_lines.append(f"[{name.upper()}] {status} — {details}")
report_text = "\n".join(report_lines)

row = {
    "timestamp": ts,
    "overall": overall,
    "docker_status": checks.get("docker", {}).get("status", ""),
    "ram_free_mb": 0,
    "ram_status": checks.get("ram", {}).get("status", ""),
    "disk_free_pct": 0,
    "disk_status": checks.get("disk", {}).get("status", ""),
    "git_status": checks.get("git", {}).get("status", ""),
    "details": json.dumps(checks, ensure_ascii=False),
    "name": f"cron_health_{file_ts}",
    "status": "success" if overall == "HEALTHY" else "error",
    "message": report_text,
}

API_URL = f"{SUPABASE_URL}/rest/v1/cron_results"
headers = {
    "Content-Type": "application/json",
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Prefer": "return=minimal",
}

print(f"Service key present: {bool(SERVICE_KEY)}")
print(f"Target: {API_URL}")

try:
    data_bytes = json.dumps(row).encode("utf-8")
    req = urllib.request.Request(API_URL, data=data_bytes, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = resp.read().decode()[:300]
        print(f"SUCCESS: HTTP {resp.status}")
        print(f"Body: {body}")
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
