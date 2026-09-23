#!/usr/bin/env python3
import json, os, urllib.request

SUPABASE_URL = 'https://bwspcsiazbwrrxpgoldx.supabase.co'
SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '')

hist_file = 'cron_results_local.json'
history = json.loads(open(hist_file).read())
last = history[-1]
ts = last.get('timestamp', '')
cron_id = last.get('cron_id', '')
checks = json.loads(last.get('details', '{}'))

row = {
    'timestamp': ts,
    'overall': last.get('overall', 'UNKNOWN'),
    'docker_status': checks.get('docker', {}).get('status', ''),
    'ram_free_mb': last.get('ram_free_mb', 0),
    'ram_status': checks.get('ram', {}).get('status', ''),
    'disk_free_pct': last.get('disk_free_pct', 0),
    'disk_status': checks.get('disk', {}).get('status', ''),
    'git_status': checks.get('git', {}).get('status', ''),
    'details': json.dumps(checks, ensure_ascii=False),
    'name': cron_id,
    'status': 'success' if last.get('overall') == 'HEALTHY' else 'error',
    'message': f'Health check {cron_id}: {last.get("overall")}',
}

print('Row to push:')
print(json.dumps(row, indent=2, ensure_ascii=False))

if SERVICE_KEY:
    print(f'\nUsing service key (len={len(SERVICE_KEY)})')
    headers = {'Content-Type': 'application/json', 'apikey': SERVICE_KEY, 'Authorization': f'Bearer {SERVICE_KEY}', 'Prefer': 'return=minimal'}
    API_URL = f'{SUPABASE_URL}/rest/v1/cron_results'
    try:
        data = json.dumps(row).encode('utf-8')
        req = urllib.request.Request(API_URL, data=data, headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f'SUCCESS: HTTP {resp.status}')
            print(f'Body: {resp.read().decode()[:200]}')
    except Exception as e:
        print(f'FAILED: {e}')
else:
    print('\nNo service key available')
