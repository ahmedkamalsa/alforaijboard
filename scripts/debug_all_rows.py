#!/usr/bin/env python3
"""Debug: read ALL rows from cron_results with pagination."""
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
        print(f'Fetched {len(rows)} rows (offset {offset}, total so far: {len(all_rows)})')
        offset += limit
        if len(rows) < limit:
            break

print(f'\nTotal rows: {len(all_rows)}')
print(f'\nLast 10 rows (newest first via created_at):')
# Sort by created_at descending
sorted_rows = sorted(all_rows, key=lambda r: r.get('created_at', ''), reverse=True)
for row in sorted_rows[:10]:
    name = row.get('name', '?')
    status = row.get('status', '?')
    msg = str(row.get('message', ''))[:100]
    created = row.get('created_at', '?')
    print(f'  [{status}] {name} — {created}')
    if msg.strip():
        print(f'    {msg}')
