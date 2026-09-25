#!/usr/bin/env python3
"""Verify: count cron_results rows, show latest 3."""
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

# Count
count_url = f'{SUPABASE_URL}/rest/v1/cron_results?limit=1000'
req = urllib.request.Request(count_url, headers=headers)
with urllib.request.urlopen(req, timeout=10) as resp:
    rows = json.loads(resp.read().decode())
    total = len(rows)
    print(f'Total cron_results rows: {total}')

# Latest 3
latest_url = f'{SUPABASE_URL}/rest/v1/cron_results?limit=3'
req2 = urllib.request.Request(latest_url, headers=headers)
with urllib.request.urlopen(req2, timeout=10) as resp2:
    latest = json.loads(resp2.read().decode())
    print(f'Latest 3 rows (newest first):')
    for row in latest:
        name = row.get('name', '?')
        status = row.get('status', '?')
        msg = str(row.get('message', ''))
        if len(msg) > 120:
            msg = msg[:120].rstrip() + '...'
        print(f'  [{status.upper()}] {name}')
        if msg.strip():
            print(f'    {msg}')
