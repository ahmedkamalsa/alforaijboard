#!/usr/bin/env python3
"""Peek at cron_results table schema + last 3 rows."""
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

# 1. Get table schema via PostgREST .json endpoint
print('=== SCHEMA (public.cron_results) ===')
try:
    r = requests.get(f'{SUPABASE_URL}/rest/v1/information_schema.columns?table_name=cron_results', headers=headers, timeout=10)
    print(f'Schema HTTP {r.status_code}')
    if r.ok:
        cols = r.json()
        for c in cols:
            print(f"  {c.get('column_name')} ({c.get('data_type')})")
    else:
        print(r.text[:300])
except Exception as e:
    print(f'Schema error: {e}')

print()
print('=== LAST 5 ROWS ===')
try:
    r2 = requests.get(f'{SUPABASE_URL}/rest/v1/cron_results?order=inserted_at.desc&limit=5', headers=headers, timeout=10)
    print(f'Rows HTTP {r2.status_code}')
    if r2.ok:
        rows = r2.json()
        print(f'Records: {len(rows)}')
        for row in rows:
            # Print compact - skip big message column
            compact = {k: v for k, v in row.items() if k not in ('message', 'details', 'checks')}
            print(f"  {compact}")
            if 'message' in row:
                msg = str(row['message'])
                print(f"    message[:120]: {msg[:120]}")
    else:
        print(r2.text[:300])
except Exception as e:
    print(f'Rows error: {e}')
