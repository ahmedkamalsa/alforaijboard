#!/usr/bin/env python3
"""CRITICAL BUG: Show that Suppabase returns rows in insertion order, not by created_at."""
import os, json, urllib.request

SUPABASE_URL = 'https://bwspcsiazbwrrxpgoldx.supabase.co'
key = os.environ.get('SUPABASE_SERVICE_KEY', '') or os.environ.get('SUPABASE_ANON_KEY', '')

if not key:
    env_path = '/c/Users/hello/alforaijboard-gh/.env'
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith('SUPABASE_SERVICE_KEY='):
                    key = line.split('=', 1)[1].strip().strip('"').strip("'")
                    break
                elif line.startswith('SUPABASE_ANON_KEY='):
                    key = line.split('=', 1)[1].strip().strip('"').strip("'")
                    break

if not key:
    print('NO KEY')
    exit(1)

headers = {'apikey': key, 'Content-Type': 'application/json'}

# Get ALL rows WITHOUT order clause — PostgREST returns in insertion order by default
print('=== All rows in insertion order (limit=200) ===')
url = f'{SUPABASE_URL}/rest/v1/cron_results?limit=200'
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=10) as resp:
    rows = json.loads(resp.read().decode())

print(f'Total rows fetched: {len(rows)}')
print()
for i, row in enumerate(rows):
    name = row.get('name', '?')
    status = row.get('status', '?')
    created = row.get('created_at', '?')
    print(f'{i+1:3d}. [{status}] {name} — {created}')

# Now try with explicit order
print()
print('=== With explicit ?order=created_at.desc ===')
url2 = f'{SUPABASE_URL}/rest/v1/cron_results?order=created_at.desc&limit=5'
req2 = urllib.request.Request(url2, headers=headers)
with urllib.request.urlopen(req2, timeout=10) as resp2:
    rows2 = json.loads(resp2.read().decode())
for row in rows2:
    name = row.get('name', '?')
    status = row.get('status', '?')
    created = row.get('created_at', '?')
    print(f'  [{status}] {name} — {created}')
