#!/usr/bin/env python3
"""Append health check result to local JSON + Supabase (if key available)."""
import json, datetime, urllib.request, os, sys

# --- Live metrics from wmic ---
FREE_RAW = 5580188
TOTAL_RAW = 16653704
free_mb = FREE_RAW // 1024
total_mb = TOTAL_RAW // 1024
ram_pct_free = round(free_mb / total_mb * 100, 1)

DISK_FREE_RAW = 22244196352
DISK_TOTAL_RAW = 210348150784
disk_free_gb = round(DISK_FREE_RAW / (1024**3), 2)
disk_total_gb = round(DISK_TOTAL_RAW / (1024**3), 2)
disk_pct_free = round(DISK_FREE_RAW / DISK_TOTAL_RAW * 100, 1)

now = datetime.datetime.utcnow()
ts = now.strftime('%Y-%m-%dT%H:%M:%S+00:00')
ts_id = now.strftime('%Y%m%d_%H%M')

entry = {
    'cron_id': f'health_{ts_id}',
    'host': 'DESKTOP-2U21BL4',
    'timestamp': ts,
    'overall': 'NEEDS_ATTENTION',
    'checks': {
        'docker': {'status': 'STOPPED', 'severity': 'error', 'details': 'Docker Desktop daemon not running'},
        'ram': {'status': 'OK', 'severity': 'info', 'details': f'{free_mb} MB free / {total_mb} MB total ({ram_pct_free}%) — threshold: 500 MB'},
        'agents': {'status': 'OK', 'severity': 'info', 'details': '1 hermes.exe + 26 python + 20 node processes running'},
        'disk': {'status': 'OK', 'severity': 'warning', 'details': f'{disk_free_gb} GB free ({disk_pct_free}%) / {disk_total_gb} GB total — threshold: 10%'},
        'git': {'status': 'DIRTY', 'severity': 'warning', 'details': '3 modified + 4 untracked files in alforaijboard repo'}
    },
    'docker_status': 'STOPPED',
    'ram_free_mb': free_mb,
    'ram_total_mb': total_mb,
    'disk_free_gb': disk_free_gb,
    'disk_total_gb': disk_total_gb,
    'disk_free_pct': disk_pct_free,
    'agent_count': 47,
    'git_dirty_count': 7,
    'git_status': 'DIRTY'
}

# 1. Local append
local_path = '/c/Users/hello/alforaijboard-gh/cron_results_local.json'
try:
    with open(local_path) as f:
        existing = json.load(f)
except Exception:
    existing = []
if not any(e.get('cron_id') == entry['cron_id'] for e in existing):
    existing.append(entry)
with open(local_path, 'w') as f:
    json.dump(existing, f, indent=2, ensure_ascii=False)
print(f'[LOCAL] Appended {entry["cron_id"]} — total: {len(existing)}')

# 2. Supabase insert (if key in env or .env file)
SUPABASE_URL = 'https://bwspcsiazbwrrxpgoldx.supabase.co'
SUPABASE_KEY = os.environ.get('SUPABASE_ANON_KEY', '') or os.environ.get('SUPABASE_SERVICE_KEY', '')

if not SUPABASE_KEY:
    env_path = '/c/Users/hello/alforaijboard-gh/.env'
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith('SUPABASE_ANON_KEY='):
                    SUPABASE_KEY = line.split('=', 1)[1].strip().strip('"').strip("'")
                    break
                elif line.startswith('SUPABASE_SERVICE_KEY='):
                    SUPABASE_KEY = line.split('=', 1)[1].strip().strip('"').strip("'")
                    break

if SUPABASE_KEY:
    url = f'{SUPABASE_URL}/rest/v1/cron_results'
    headers = {
        'apikey': SUPABASE_KEY,
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    req = urllib.request.Request(url, data=json.dumps(entry).encode('utf-8'), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode()[:300]
            print(f'[SUPA] HTTP {resp.status} — inserted to cron_results: {body}')
    except Exception as e:
        print(f'[SUPA] Failed: {e}')
else:
    print('[SUPA] Skipped — no Supabase key found in env or .env')
