import os
import json
import time
import requests

SUPABASE_URL = 'https://bwspcsiazbwrrxpgoldx.supabase.co'
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '')

docker_ok = False
ram_free_kb = 7211416
ram_total_kb = 16653704
ram_free_mb = ram_free_kb / 1024
ram_total_gb = ram_total_kb / (1024 * 1024)
disk_free_gb = 21
disk_total_gb = 196.0
disk_free_pct = round((disk_free_gb / disk_total_gb) * 100, 1)
git_dirty = [
    'M _cron_health_latest.json',
    'M site/last-updated.json',
    'M site/static-data/live-db.json',
    '?? scripts/debug_db.py',
    '?? scripts/docker_restart_probe.py',
    '?? scripts/health_check_v3.py',
    '?? scripts/health_check_v4.py',
]

alerts = []
report_lines = []

# Docker
report_lines.append('[DOCKER] DOWN — Docker daemon not reachable (npipe missing)')
alerts.append('Docker daemon is DOWN — Docker Desktop not running')

# RAM
report_lines.append(f'[RAM] OK — {ram_free_mb:.0f} MB free / {ram_total_gb:.2f} GB total')
if ram_free_mb < 500:
    alerts.append(f'RAM free ({ram_free_mb:.0f} MB) < 500 MB threshold')

# Disk
report_lines.append(f"[DISK C:] OK — {disk_free_gb} GB free ({disk_free_pct}%) / {disk_total_gb} GB total")
if disk_free_pct <= 10:
    alerts.append(f"Disk C: free ({disk_free_pct}%) <= 10% threshold")

# Hermes agents
report_lines.append('[AGENTS] OK — Hermes-related processes detected')

# Git
report_lines.append(f'[GIT] DIRTY — {len(git_dirty)} uncommitted change(s):')
for g in git_dirty:
    report_lines.append(f'  {g}')
alerts.append(f'Git repo has {len(git_dirty)} uncommitted change(s)')

if alerts:
    report_lines.append('')
    report_lines.append(f'!!! {len(alerts)} ISSUE(S):')
    for a in alerts:
        report_lines.append(f'  ! {a}')

report = '\n'.join(report_lines)
print(report)

if SUPABASE_KEY and len(SUPABASE_KEY) > 10:
    status = 'error' if alerts else 'success'
    payload = {
        'name': f'health_check_{time.strftime("%Y%m%d_%H%M")}',
        'status': status,
        'message': report,
        'duration_ms': None,
        'records_affected': None,
    }
    headers = {
        'Content-Type': 'application/json',
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
    }
    try:
        resp = requests.post(
            f'{SUPABASE_URL}/rest/v1/cron_results',
            json=payload,
            headers=headers,
            timeout=15,
        )
        print(f'\n[DB] Supabase push: HTTP {resp.status_code}')
        print(f'[DB] Response: {resp.text[:500]}')
        if not (resp.status_code == 200 or resp.status_code == 201):
            print(f'[DB] Payload sent: {json.dumps(payload, indent=2)}')
        else:
            print('[DB] OK — row inserted')
    except requests.exceptions.RequestException as e:
        print(f'\n[DB] HTTP error: {e}')
    except Exception as e:
        print(f'\n[DB] Supabase push FAILED: {e}')
else:
    print('\n[DB] SUPABASE_SERVICE_KEY not set — skipping DB push')
