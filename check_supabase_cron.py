#!/usr/bin/env python3
"""Check Supabase cron_results table for historical entries."""
import json, urllib.request, urllib.error

url = 'https://bwspcsiazbwrrxpgoldx.supabase.co/rest/v1/cron_results?select=id,name,status,created_at&order=created_at.desc&limit=10'
headers = {
    'apikey': 'sb_publishable_c84oHQS94osRqw_SiTIqMg_8icxvatZ',
    'Authorization': 'Bearer sb_publishable_c84oHQS94osRqw_SiTIqMg_8icxvatZ',
}

try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
    print(f"Rows in cron_results: {len(data)}")
    for row in data:
        print(f"  id={row['id']}  name={row['name']}  status={row['status']}  created_at={row['created_at'][:19]}")
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.read().decode()[:200]}")
except Exception as e:
    print(f"Error: {e}")
