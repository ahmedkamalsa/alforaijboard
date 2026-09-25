import os
import json
import requests
import sys

SUPABASE_URL = 'https://bwspcsiazbwrrxpgoldx.supabase.co'
key = os.environ.get('SUPABASE_SERVICE_KEY', '')

url = f'{SUPABASE_URL}/rest/v1/cron_results?select=id,cron_id,timestamp,overall,docker_status,ram_free_mb,disk_free_pct,git_status&order=timestamp.desc&limit=3'
headers = {
    'Content-Type': 'application/json',
    'apikey': key,
}

try:
    r = requests.get(url, headers=headers, timeout=15)
    print(f'HTTP {r.status_code}')
    if r.ok:
        data = r.json()
        print(f'Records returned: {len(data)}')
        for row in data:
            print(f"  id={row.get('id','?')} cron_id={row.get('cron_id','?')} ts={row.get('timestamp','?')} overall={row.get('overall','?')} docker={row.get('docker_status','?')} ram_mb={row.get('ram_free_mb','?')} disk_pct={row.get('disk_free_pct','?')} git={row.get('git_status','?')}")
    else:
        print(r.text[:500])
except Exception as e:
    print(f'ERROR: {type(e).__name__}: {e}')
    sys.exit(1)

