#!/usr/bin/env python3
"""Test Supabase insert with raw payload."""
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

payload = {
    'name': 'test_insert_manual_' + __import__('datetime').datetime.utcnow().strftime('%Y%m%d_%H%M'),
    'status': 'success',
    'message': 'Manual test insert from debug script',
}

url = f'{SUPABASE_URL}/rest/v1/cron_results'
headers = {
    'apikey': key,
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal'
}

req = urllib.request.Request(url, json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = resp.read().decode()[:300]
        print(f'HTTP {resp.status}: {body}')
except Exception as e:
    print(f'FAILED: {e}')
    # Try without Prefer header
    headers2 = {'apikey': key, 'Content-Type': 'application/json'}
    req2 = urllib.request.Request(url, json.dumps(payload).encode('utf-8'), headers=headers2, method='POST')
    try:
        with urllib.request.urlopen(req2, timeout=15) as resp2:
            body2 = resp2.read().decode()[:300]
            print(f'HTTP {resp2.status} (no prefer): {body2}')
    except Exception as e2:
        print(f'ALSO FAILED: {e2}')
