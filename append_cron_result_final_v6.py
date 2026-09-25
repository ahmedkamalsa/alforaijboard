#!/usr/bin/env python3
"""Final health check v6 — clean append to Supabase + local JSON."""
import json, datetime, os
import urllib.request

# --- Live metrics (from wmic) ---
FREE_RAW = 5651552
TOTAL_RAW = 16653704
free_mb = FREE_RAW // 1024
total_mb = TOTAL_RAW // 1024
ram_pct = round(free_mb / total_mb * 100, 1)

DISK_FREE_RAW = 22242697216
DISK_TOTAL_RAW = 210348150784
disk_free_gb = round(DISK_FREE_RAW / (1024**3), 2)
disk_total_gb = round(DISK_TOTAL_RAW / (1024**3), 2)
disk_pct = round(DISK_FREE_RAW / DISK_TOTAL_RAW * 100, 1)

now = datetime.datetime.utcnow()
ts = now.strftime('%Y-%m-%dT%H:%M:%S+00:00')
ts_id = now.strftime('%Y%m%d_%H%M')

# Build the alert message
checks_text = (
    f"Docker: STOPPED — daemon not reachable via npipe.\n"
    f"RAM: {free_mb} MB free / {total_mb} MB total ({ram_pct}%) — OK (above 500 MB threshold).\n"
    f"Agents: 1 hermes.exe (PID 9448) + 26 python + 20 node processes running — OK.\n"
    f"Disk C:: {disk_free_gb} GB free ({disk_pct}%) / {disk_total_gb} GB total — OK but borderline, warrants monitoring.\n"
    f"Git (alforaijboard): DIRTY — 3 modified + 4 untracked files (uncommitted changes)."
)

entry = {
    'name': f'health_{ts_id}',
    'status': 'error',
    'message': checks_text,
    'docker_status': 'STOPPED',
    'ram_free_mb': free_mb,
    'ram_total_mb': total_mb,
    'disk_free_gb': disk_free_gb,
    'disk_total_gb': disk_total_gb,
    'disk_free_pct': disk_pct,
    'agent_count': 47,
    'git_dirty_count': 7,
    'git_status': 'DIRTY',
    'overall': 'NEEDS_ATTENTION'
}

# 1. Local append
local_path = '/c/Users/hello/alforaijboard-gh/cron_results_local.json'
try:
    with open(local_path) as f:
        existing = json.load(f)
except Exception:
    existing = []
existing.append(entry)
MAX_LOCAL = 60
if len(existing) > MAX_LOCAL:
    existing = existing[-MAX_LOCAL:]
with open(local_path, 'w') as f:
    json.dump(existing, f, indent=2, ensure_ascii=False)
print(f'[LOCAL] Appended {entry["name"]} — total: {len(existing)}')

# 2. Supabase insert
SUPABASE_URL = 'https://bwspcsiazbwrrxpgoldx.supabase.co'
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '') or os.environ.get('SUPABASE_ANON_KEY', '')

if not SUPABASE_KEY:
    env_path = '/c/Users/hello/alforaijboard-gh/.env'
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith('SUPABASE_SERVICE_KEY='):
                    SUPABASE_KEY = line.split('=', 1)[1].strip().strip('"').strip("'")
                    break
                elif line.startswith('SUPABASE_ANON_KEY='):
                    SUPABASE_KEY = line.split('=', 1)[1].strip().strip('"').strip("'")
                    break

if SUPABASE_KEY:
    url = f'{SUPABASE_URL}/rest/v1/cron_results'
    headers = {
        'apikey': SUPABASE_KEY,
        'Content-Type': 'application/json',
    }
    payload = {
        'name': entry['name'],
        'status': entry['status'],
        'message': entry['message'],
    }
    req = urllib.request.Request(url, json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f'[SUPA] HTTP {resp.status} — inserted: {entry["name"]}')
    except Exception as e:
        print(f'[SUPA] Failed: {e}')
else:
    print('[SUPA] Skipped — no key')
