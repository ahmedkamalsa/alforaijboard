#!/usr/bin/env python3
"""Push health check to Supabase with retries."""
import os, datetime, json, time
import urllib.request, urllib.error

report_path = 'C:\\Users\\hello\\alforaijboard-gh\\health_report.txt'
json_path = 'C:\\Users\\hello\\alforaijboard-gh\\health_report.json'

with open(report_path) as f:
    report_text = f.read()

with open(json_path) as f:
    json_data = json.load(f)

supabase_url = os.environ.get('SUPABASE_URL', 'https://bwspcsiazbwrrxpgoldx.supabase.co')
service_key = os.environ.get('SUPABASE_SERVICE_KEY') or os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

payload = {
    'name': f'health_check_{datetime.datetime.now().strftime("%Y%m%d_%H%M")}',
    'status': 'warning' if json_data.get('alerts') else 'success',
    'message': report_text.strip(),
    'duration_ms': None,
    'records_affected': None,
}

body = json.dumps(payload).encode('utf-8')
endpoint = f'{supabase_url}/rest/v1/cron_results'

headers = {
    'Content-Type': 'application/json',
    'apikey': service_key,
    'Authorization': f'Bearer {service_key}',
    'Prefer': 'return=minimal',
}

for attempt in range(3):
    print(f'Attempt {attempt + 1}/3: POST {endpoint}')
    try:
        req = urllib.request.Request(endpoint, data=body, headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=30) as resp:
            code = resp.status
            resp_body = resp.read().decode('utf-8')
            print(f'HTTP {code}')
            if code in (200, 201):
                print('SUCCESS: Pushed to Supabase cron_results')
                print(f'ID: {resp_body[:100]}')
                break
            else:
                print(f'Response: {resp_body[:200]}')
    except urllib.error.HTTPError as e:
        print(f'HTTP {e.code}: {e.read().decode("utf-8")[:200]}')
        break
    except Exception as e:
        print(f'Error: {e}')
        if attempt < 2:
            print('Retrying in 3s...')
            time.sleep(3)
        else:
            print('All attempts failed')
