#!/usr/bin/env python3
"""Show trend summary of health checks."""
import json, pathlib
from datetime import datetime

results_dir = pathlib.Path('/c/Users/hello/alforaijboard-gh/cron_results')
all_files = sorted(results_dir.glob('cron_results_*.json'))

records = []
for f in all_files:
    data = json.loads(f.read_text(encoding='utf-8'))
    ts = data.get('timestamp', '')
    try:
        dt = datetime.fromisoformat(ts)
    except:
        dt = None
    records.append((dt, data))

print(f'Total historical records: {len(records)}')
print()

for dt, data in reversed(records[-5:]):
    ts = dt.isoformat() if dt else 'unknown'
    ch = data.get('checks', {})
    overall = data.get('overall', '?')
    docker = ch.get('docker', {}).get('status', '?')
    ram = ch.get('ram', {}).get('free_mb', '?')
    disk_free = ch.get('disk', {}).get('free_gb', '?')
    git = ch.get('git', {}).get('status', '?')
    print(f'[{ts}] overall={overall} docker={docker} ram={ram}MB disk_free={disk_free}GB git={git}')

print()
print('Recent trend:')
for dt, data in reversed(records[-12:]):
    ts = dt.isoformat() if dt else 'unknown'
    docker = data.get('checks',{}).get('docker',{}).get('status','?')
    overall = data.get('overall','?')
    print(f'  {ts}  docker={docker}  overall={overall}')
