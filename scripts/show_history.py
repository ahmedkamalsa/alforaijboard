#!/usr/bin/env python3
import json
from pathlib import Path

hist = Path('cron_results_local.json')
data = json.loads(hist.read_text())
print(f'Total entries: {len(data)}')
print('Last 5 entries:')
for e in data[-5:]:
    print(f'  {e["cron_id"]} — {e["overall"]} — docker={e["docker_status"]} disk={e["disk_free_pct"]}% git={e["git_status"]}')
