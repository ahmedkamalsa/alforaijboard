#!/usr/bin/env python3
import json
data = json.load(open('/c/Users/hello/alforaijboard-gh/cron_results_local.json'))
print('Entries in cron_results_local.json:', len(data))
for e in data:
    cid = e.get('cron_id', 'NO_CRON_ID')
    ts = e.get('timestamp', 'NO_TS')
    ov = e.get('overall', 'NO_OVERALL')
    print(f'  {cid}  {ts}  {ov}')
