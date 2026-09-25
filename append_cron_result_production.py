#!/usr/bin/env python3
"""Final health check — clean append to cron_results (only name/status/message)."""
import json, datetime, os
import urllib.request

# --- Live metrics (from this run's wmic) ---
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

# Build readable report
report = (
    f"=== SYSTEM HEALTH REPORT — {now.strftime('%Y-%m-%d %H:%M')} UTC ===\n"
    f"Host: DESKTOP-2U21BL4\n\n"
    f"[1] DOCKER: DOWN (critical)\n"
    f"    Docker Desktop daemon not reachable via npipe.\n\n"
    f"[2] RAM: OK (info)\n"
    f"    {free_mb} MB free / {total_mb} MB total ({ram_pct}%)\n"
    f"    Above 500 MB threshold.\n\n"
    f"[3] HERMES AGENTS: OK (info)\n"
    f"    1 hermes.exe (PID 9448) + 26 python + 20 node processes running.\n\n"
    f"[4] DISK C:: WARNING — borderline\n"
    f"    {disk_free_gb} GB free ({disk_pct}%) / {disk_total_gb} GB total.\n"
    f"    Above 10% threshold but close — warrants monitoring.\n\n"
    f"[5] GIT (alforaijboard): DIRTY (warning)\n"
    f"    3 modified + 4 untracked files — uncommitted changes.\n"
)

entry_name = f'health_{ts_id}'
entry_status = 'error'
entry_message = report

# 1. Local JSON
local_path = '/c/Users/hello/alforaijboard-gh/cron_results_local.json'
try:
    with open(local_path) as f:
        existing = json.load(f)
except Exception:
    existing = []
local_entry = {
    'cron_id': entry_name,
    'timestamp': ts,
    'overall': 'NEEDS_ATTENTION',
    'docker': 'DOWN',
    'ram_free_mb': free_mb,
    'disk_free_pct': disk_pct,
    'git_status': 'DIRTY',
    'agent_count': 47,
    'report': report
}
existing.append(local_entry)
MAX_LOCAL = 60
if len(existing) > MAX_LOCAL:
    existing = existing[-MAX_LOCAL:]
with open(local_path, 'w') as f:
    json.dump(existing, f, indent=2, ensure_ascii=False)
print(f'[LOCAL] Appended {entry_name} — total: {len(existing)}')

# 2. Supabase
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
    headers = {'apikey': SUPABASE_KEY, 'Content-Type': 'application/json'}
    payload = {'name': entry_name, 'status': entry_status, 'message': entry_message}
    req = urllib.request.Request(url, json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f'[SUPA] HTTP {resp.status} — inserted: {entry_name}')
    except Exception as e:
        print(f'[SUPA] Failed: {e}')
else:
    print('[SUPA] Skipped — no key')
