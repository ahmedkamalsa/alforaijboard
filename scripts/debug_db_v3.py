#!/usr/bin/env python3
"""Discover cron_results table columns + last rows."""
import os, json, requests, sys

SUPABASE_URL = 'https://bwspcsiazbwrrxpgoldx.supabase.co'
key = os.environ.get('SUPABASE_SERVICE_KEY', '')

if not key:
    env_path = '/c/Users/hello/alforaijboard-gh/.env'
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith('SUPABASE_SERVICE_KEY='):
                    key = line.split('=', 1)[1].strip().strip('"').strip("'")
                    break

if not key:
    print('No Supabase key found')
    sys.exit(1)

headers = {'apikey': key, 'Content-Type': 'application/json'}

# Discover columns by selecting all and inspecting first row
print('=== DISCOVERING COLUMNS ===')
try:
    r = requests.get(f'{SUPABASE_URL}/rest/v1/cron_results?limit=1', headers=headers, timeout=10)
    print(f'HTTP {r.status_code}')
    if r.ok:
        row = r.json()
        if row:
            print(f'Columns ({len(row)}):')
            for k in row.keys():
                print(f'  - {k}')
        else:
            print('Table empty (no rows)')
    else:
        print(f'Error: {r.text[:300]}')
except Exception as e:
    print(f'Error: {e}')

print()
print('=== LAST 5 ROWS (compact) ===')
try:
    r2 = requests.get(f'{SUPABASE_URL}/rest/v1/cron_results?limit=10', headers=headers, timeout=10)
    print(f'HTTP {r2.status_code}')
    if r2.ok:
        rows = r2.json()
        print(f'Records returned: {len(rows)}')
        for i, row in enumerate(rows):
            print(f'--- Row {i+1} ---')
            for k, v in row.items():
                sv = str(v)
                if len(sv) > 80:
                    sv = sv[:80] + '...'
                print(f'  {k}: {sv}')
    else:
        print(f'Error: {r2.text[:300]}')
except Exception as e:
    print(f'Error: {e}')
