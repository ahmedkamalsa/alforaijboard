#!/usr/bin/env python3
"""Distribution analysis for health check history."""
import json, pathlib
from collections import Counter

results_dir = pathlib.Path('/c/Users/hello/alforaijboard-gh/cron_results')
all_files = sorted(results_dir.glob('cron_results_*.json'))

records = []
for f in all_files:
    data = json.loads(f.read_text(encoding='utf-8'))
    records.append(data)

docker_statuses = Counter(r.get('checks',{}).get('docker',{}).get('status','?') for r in records)
overall = Counter(r.get('overall','?') for r in records)
git_statuses = Counter(r.get('checks',{}).get('git',{}).get('status','?') for r in records)

print(f'Total: {len(records)} reads')
print()
print('Docker status distribution:')
for status, count in docker_statuses.most_common():
    print(f'  {status}: {count}')
print()
print('Git status distribution:')
for status, count in git_statuses.most_common():
    print(f'  {status}: {count}')
print()
print('Overall distribution:')
for status, count in overall.most_common():
    print(f'  {status}: {count}')
print()
print('Alert/warning threshold summary (last 10):')
for r in records[-10:]:
    ts = r.get('timestamp','?')
    ch = r.get('checks',{})
    issues = []
    d = ch.get('docker',{})
    if d.get('status') != 'running':
        issues.append('DOCKER_DOWN')
    ram = ch.get('ram',{})
    if ram.get('free_mb', 1e9) < 500:
        issues.append(f'RAM_LOW({ram.get("free_mb")}MB)')
    disk = ch.get('disk',{})
    fp = disk.get('free_pct', 100)
    if fp < 10:
        issues.append(f'DISK_LOW({fp}%)')
    if ch.get('git',{}).get('status') == 'dirty':
        issues.append('GIT_DIRTY')
    print(f'  {ts}  {"; ".join(issues) if issues else "OK"}')
