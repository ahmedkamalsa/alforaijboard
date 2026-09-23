#!/usr/bin/env python3
"""Debug: show exact HTTP request/response to Supabase."""
import json, os, urllib.request, urllib.error

SUPABASE_URL = 'https://bwspcsiazbwrrxpgoldx.supabase.co'
SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '')

print(f"Service key (first 10 chars): {SERVICE_KEY[:10] if SERVICE_KEY else 'MISSING'}...")
print(f"Service key length: {len(SERVICE_KEY) if SERVICE_KEY else 0}")

# Try a minimal POST with just name and status (required fields per table schema)
row = {
    "name": "cron_health_test_20260922_1215",
    "status": "success",
    "message": "Test push from health cron",
    "timestamp": "2026-09-22T12:15:00Z",
    "overall": "HEALTHY",
    "docker_status": "RUNNING",
    "ram_free_mb": 4500.0,
    "ram_status": "OK",
    "disk_free_pct": 12.2,
    "disk_status": "OK",
    "git_status": "CLEAN",
    "details": "{\"docker\":{\"status\":\"RUNNING\",\"severity\":\"info\",\"details\":\"Test\"}}",
}

API_URL = f"{SUPABASE_URL}/rest/v1/cron_results"
headers = {
    "Content-Type": "application/json",
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Prefer": "return=minimal",
}

print(f"\nPOST {API_URL}")
print(f"Headers: {headers}")
print(f"Body: {json.dumps(row, indent=2)}")

try:
    data = json.dumps(row).encode("utf-8")
    req = urllib.request.Request(API_URL, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = resp.read().decode()
        print(f"\nSUCCESS: HTTP {resp.status}")
        print(f"Body: {body}")
except urllib.error.HTTPError as e:
    print(f"\nHTTP ERROR: {e.code} {e.reason}")
    print(f"Response body: {e.read().decode()[:500]}")
except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
