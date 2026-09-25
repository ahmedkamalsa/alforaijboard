#!/usr/bin/env python3
"""Show latest local cron entry."""
import json

with open('/c/Users/hello/alforaijboard-gh/cron_results_local.json') as f:
    data = json.load(f)

print(f'Local entries: {len(data)}')
last = data[-1]
print(f'Last entry cron_id: {last.get("cron_id")}')
print(f'Overall: {last.get("overall")}')
print(f'Docker: {last.get("docker","?")}')
print(f'RAM free: {last.get("ram_free_mb")} MB')
print(f'Disk free: {last.get("disk_free_pct")}%')
print(f'Git: {last.get("git_status","?")}')
print(f'Agent count: {last.get("agent_count")}')
