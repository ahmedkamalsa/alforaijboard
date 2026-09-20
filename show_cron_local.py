#!/usr/bin/env python3
import json
data = json.load(open('/c/Users/hello/alforaijboard-gh/cron_results_local.json'))
print('Entries in cron_results_local.json:', len(data))
for e in data:
    print(f"  {e['cron_id']}  {e['timestamp']}  {e['overall']}")
