#!/usr/bin/env python3
"""Show latest local cron result entry."""
import json

with open('/c/Users/hello/alforaijboard-gh/cron_results_local.json') as f:
    data = json.load(f)

print(f'Local entries: {len(data)}')
if data:
    last = data[-1]
    print(f'Last entry:')
    print(f'  cron_id: {last.get("cron_id")}')
    print(f'  timestamp: {last.get("timestamp")}')
    print(f'  overall: {last.get("overall")}')
    print(f'  docker_status: {last.get("docker_status")}')
    print(f'  ram_free_mb: {last.get("ram_free_mb")}')
    print(f'  disk_free_pct: {last.get("disk_free_pct")}')
    print(f'  git_status: {last.get("git_status")}')
