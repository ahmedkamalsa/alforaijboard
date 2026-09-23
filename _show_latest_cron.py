#!/usr/bin/env python3
"""Read and display the latest cron health result."""
import json, pathlib

p = pathlib.Path('/c/Users/hello/alforaijboard-gh/cron_results')
found = sorted(p.glob('cron_results_*.json'))

if not found:
    print('no cron result files')
else:
    for f in found:
        print(f'- {f.name} ({f.stat().st_size} bytes)')
    latest = found[-1]
    print('---' + latest.name + '---')
    data = json.loads(latest.read_text(encoding='utf-8'))
    print(json.dumps(data, indent=2, ensure_ascii=False))
