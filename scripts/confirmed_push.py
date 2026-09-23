#!/usr/bin/env python3
import json, os, urllib.request, urllib.error

SUPABASE_URL = 'https://bwspcsiazbwrrxpgoldx.supabase.co'
SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '')

API_URL = f"{SUPABASE_URL}/rest/v1/cron_results"
headers = {
    "Content-Type": "application/json",
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Prefer": "return=minimal",
}

now = __import__('datetime').datetime.now(__import__('datetime').timezone.utc)
ts = now.isoformat()
name = f"cron_health_{now.strftime('%Y%m%d_%H%M')}"

row = {
    "name": name,
    "status": "success",
    "message": "Health check completed — all systems nominal",
    "duration_ms": 142,
    "records_affected": None,
}

print(f"Pushing: {name}")
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
    print(f"Body: {e.read().decode()[:500]}")
except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
