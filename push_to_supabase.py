#!/usr/bin/env python3
"""Push health check result to Supabase cron_results table."""
import os, datetime, json
import urllib.request, urllib.error

# Read the health report
cwd = os.getcwd()
report_path = os.path.join(cwd, 'health_report.txt')
json_path = os.path.join(cwd, 'health_report.json')

if not os.path.exists(report_path):
    appdata = os.environ.get('LOCALAPPDATA', 'C:\\Users\\hello\\AppData\\Local')
    scratch = os.path.join(appdata, 'hermes', 'cache', 'scratch')
    report_path = os.path.join(scratch, 'health_report.txt')
    json_path = os.path.join(scratch, 'health_report.json')

with open(report_path) as f:
    report_text = f.read()

with open(json_path) as f:
    json_data = json.load(f)

supabase_url = os.environ.get('SUPABASE_URL', 'https://bwspcsiazbwrrxpgoldx.supabase.co')
service_key = os.environ.get('SUPABASE_SERVICE_KEY') or os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

if not service_key or len(service_key) < 20:
    print('ERROR: No valid Supabase service key found')
    print(f'  SUPABASE_URL={supabase_url}')
    print(f'  Key present={bool(service_key)}, len={len(service_key) if service_key else 0}')
    exit(1)

table = 'cron_results'
endpoint = f'{supabase_url}/rest/v1/{table}'

payload = {
    'name': f'health_check_{datetime.datetime.now().strftime("%Y%m%d_%H%M")}',
    'status': 'warning' if json_data.get('alerts') else 'success',
    'message': report_text.strip(),
    'duration_ms': None,
    'records_affected': None,
}

body = json.dumps(payload).encode('utf-8')

req = urllib.request.Request(
    endpoint,
    data=body,
    headers={
        'Content-Type': 'application/json',
        'apikey': service_key,
        'Authorization': f'Bearer {service_key}',
        'Prefer': 'return=minimal',
    },
    method='POST',
)

print(f'Pushing to Supabase: {endpoint}')
print(f'Status: {payload["status"]}')
print()

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        status_code = resp.status
        resp_body = resp.read().decode('utf-8')
        print(f'HTTP {status_code}')
        if status_code in (200, 201):
            print('SUCCESS: Health report pushed to Supabase cron_results')
            print(f'Response: {resp_body[:200]}')
        else:
            print(f'UNEXPECTED: Status {status_code}')
            print(f'Response: {resp_body[:200]}')
except urllib.error.HTTPError as e:
    print(f'HTTP Error {e.code}: {e.reason}')
    print(f'Response: {e.read().decode("utf-8")[:300]}')
except Exception as e:
    print(f'Error: {e}')
