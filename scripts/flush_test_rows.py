#!/usr/bin/env python3
"""Flush all cron_results test entries (keep only real health_check entries)."""
import os, json, urllib.request, time

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

# Fetch all rows
all_rows = []
offset = 0
limit = 100
while True:
    url = f'{SUPABASE_URL}/rest/v1/cron_results?limit={limit}&offset={offset}'
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        rows = json.loads(resp.read().decode())
        if not rows:
            break
        all_rows.extend(rows)
        offset += limit
        if len(rows) < limit:
            break

print(f'Total rows: {len(all_rows)}')

# Identify rows to delete: anything NOT starting with 'health_check' or 'cron_health'
to_delete = []
keep = []
for row in all_rows:
    name = row.get('name', '')
    if name.startswith('health_check') or name.startswith('cron_health'):
        keep.append(row)
    else:
        to_delete.append(row)

print(f'Rows to KEEP: {len(keep)}')
print(f'Rows to DELETE: {len(to_delete)}')

# Delete each row by ID
deleted = 0
for row in to_delete:
    rid = row.get('id')
    if not rid:
        continue
    del_url = f'{SUPABASE_URL}/rest/v1/cron_results?id=eq.{rid}'
    del_req = urllib.request.Request(del_url, headers={**headers, 'Prefer': 'return=minimal'}, method='DELETE')
    try:
        with urllib.request.urlopen(del_req, timeout=10) as resp:
            if resp.status in (200, 204):
                deleted += 1
    except Exception as e:
        print(f'Failed to delete id={rid}: {e}')
    time.sleep(0.1)  # be gentle

print(f'Deleted: {deleted}')
print(f'Remaining: {len(all_rows) - deleted}')

# Verify
verify_url = f'{SUPABASE_URL}/rest/v1/cron_results?limit=100'
req_v = urllib.request.Request(verify_url, headers=headers)
with urllib.request.urlopen(req_v, timeout=10) as resp_v:
    remaining = json.loads(resp_v.read().decode())
    print(f'Actual remaining: {len(remaining)}')
    for row in remaining[:5]:
        print(f'  [{row.get("status")}] {row.get("name")}')
