#!/usr/bin/env python3
import json, os, urllib.request, urllib.error

SUPABASE_URL = 'https://bwspcsiazbwrrxpgoldx.supabase.co'
SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '')

row = {
    "name": "cron_health_test_20260922_1215b",
    "status": "success",
    "message": "Test push without details column",
    "timestamp": "2026-09-22T12:15:00Z",
    "overall": "HEALTHY",
    "docker_status": "RUNNING",
    "ram_free_mb": 4500.0,
    "ram_status": "OK",
    "disk_free_pct": 12.2,
    "disk_status": "OK",
    "git_status": "CLEAN",
}

API_URL = f"{SUPABASE_URL}/rest/v1/cron_results"
headers = {
    "Content-Type": "application/json",
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Prefer": "return=minimal",
}

print(f"POST {API_URL}")
try:
    data = json.dumps(row).encode("utf-8")
    req = urllib.request.Request(API_URL, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = resp.read().decode()
        print(f"SUCCESS: HTTP {resp.status}")
        print(f"Body: {body}")
except urllib.error.HTTPError as e:
    print(f"HTTP ERROR: {e.code} {e.reason}")
    print(f"Body: {e.read().decode()[:500]}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
