#!/usr/bin/env python3
import json, os, urllib.request, urllib.error

SUPABASE_URL = 'https://bwspcsiazbwrrxpgoldx.supabase.co'
SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '')

API_URL = f"{SUPABASE_URL}/rest/v1/cron_results"
headers = {
    "Content-Type": "application/json",
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
}

print("GET /rest/v1/cron_results?limit=1")
try:
    req = urllib.request.Request(API_URL + "?limit=1", headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = resp.read().decode()
        data = json.loads(body)
        print(f"SUCCESS: HTTP {resp.status}")
        print(f"Row count: {len(data) if isinstance(data, list) else 'array'}")
        if data:
            print(f"Columns: {list(data[0].keys())}")
            print(f"First row: {json.dumps(data[0], indent=2, ensure_ascii=False)}")
except urllib.error.HTTPError as e:
    print(f"HTTP ERROR: {e.code} {e.reason}")
    print(f"Body: {e.read().decode()[:500]}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
