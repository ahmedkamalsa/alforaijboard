#!/usr/bin/env python3
"""Show current Supabase cron_results entries."""
import json, os, urllib.request, urllib.error

SUPABASE_URL = 'https://bwspcsiazbwrrxpgoldx.supabase.co'
SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '')

API_URL = f"{SUPABASE_URL}/rest/v1/cron_results?order=created_at.desc&limit=10"
headers = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
}

print(f"Fetching last 10 entries from {API_URL}")
try:
    req = urllib.request.Request(API_URL, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
        print(f"\nGot {len(data)} entries:\n")
        for row in data:
            print(f"  [{row.get('status','?')}] {row.get('name','?')} — {row.get('created_at','?')[:16]}")
            msg = (row.get('message','') or '')[:120].replace('\n',' | ')
            print(f"       {msg}")
            print()
except urllib.error.HTTPError as e:
    print(f"HTTP ERROR: {e.code} {e.reason}")
    print(f"Body: {e.read().decode()[:300]}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
