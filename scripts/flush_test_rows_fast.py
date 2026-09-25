#!/usr/bin/env python3
"""Flush test rows from cron_results — fast batch delete."""
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

# Fetch all in one call
url = f'{SUPABASE_URL}/rest/v1/cron_results?limit=200'
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=15) as resp:
    all_rows = json.loads(resp.read().decode())

print(f'Total rows: {len(all_rows)}')

# Identify rows to delete
to_delete_ids = []
for row in all_rows:
    name = row.get('name', '')
    if not (name.startswith('health_check') or name.startswith('cron_health')):
        to_delete_ids.append(str(row.get('id')))

print(f'Rows to DELETE: {len(to_delete_ids)}')
print(f'Rows to KEEP: {len(all_rows) - len(to_delete_ids)}')

if not to_delete_ids:
    print('Nothing to delete.')
    exit(0)

# Batch delete via OR filter
id_filter = 'or'.join([f'id=eq.{iid}' for iid in to_delete_ids])
del_url = f'{SUPABASE_URL}/rest/v1/cron_results?{id_filter}'
del_req = urllib.request.Request(del_url, headers={**headers, 'Prefer': 'return=minimal'}, method='DELETE')
try:
    with urllib.request.urlopen(del_req, timeout=15) as resp:
        status = resp.status
        body = resp.read().decode()[:200]
        print(f'Delete HTTP {status}: {body}')
except Exception as e:
    print(f'Delete failed: {e}')

# Verify
verify_url = f'{SUPABASE_URL}/rest/v1/cron_results?limit=10'
req_v = urllib.request.Request(verify_url, headers=headers)
with urllib.request.urlopen(req_v, timeout=10) as resp_v:
    remaining = json.loads(resp_v.read().decode())
    print(f'Remaining rows: {len(remaining)}')
    for row in remaining:
        print(f'  [{row.get("status")}] {row.get("name")} — {row.get("created_at")}')
