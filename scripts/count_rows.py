#!/usr/bin/env python3
"""Count cron_results rows."""
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
url = f'{SUPABASE_URL}/rest/v1/cron_results?limit=200'
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=10) as resp:
    rows = json.loads(resp.read().decode())
    print(f'Total rows fetched: {len(rows)}')
