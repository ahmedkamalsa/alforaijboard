#!/usr/bin/env python3
"""Repeated Supabase insert test to debug ordering."""
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

for i in range(3):
    payload = {
        'name': f'test_ordering_{i}_{int(time.time())}',
        'status': 'success',
        'message': f'Insert #{i} at {time.time()}',
    }
    url = f'{SUPABASE_URL}/rest/v1/cron_results'
    req = urllib.request.Request(url, json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f'Insert #{i}: HTTP {resp.status}')
    except Exception as e:
        print(f'Insert #{i} FAILED: {e}')
    time.sleep(0.5)

# Now read back
print()
print('Reading back last 5:')
url2 = f'{SUPABASE_URL}/rest/v1/cron_results?limit=5'
req2 = urllib.request.Request(url2, headers=headers)
with urllib.request.urlopen(req2, timeout=10) as resp2:
    rows = json.loads(resp2.read().decode())
    for row in rows:
        name = row.get('name', '?')
        status = row.get('status', '?')
        msg = str(row.get('message', ''))[:80]
        print(f'  [{status}] {name} — {msg}')
