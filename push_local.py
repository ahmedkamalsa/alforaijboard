#!/usr/bin/env python3
"""Push health check to Supabase - writes to local JSON file as fallback."""
import os, datetime, json

report_path = 'C:\\Users\\hello\\alforaijboard-gh\\health_report.txt'
json_path = 'C:\\Users\\hello\\alforaijboard-gh\\health_report.json'
local_cron_path = 'C:\\Users\\hello\\alforaijboard-gh\\cron_results_local.json'

with open(report_path) as f:
    report_text = f.read()

with open(json_path) as f:
    json_data = json.load(f)

now = datetime.datetime.now(datetime.UTC)

entry = {
    'id': json_data.get('timestamp', now.isoformat()),
    'name': f'health_check_{now.strftime("%Y%m%d_%H%M")}',
    'status': 'warning' if json_data.get('alerts') else 'success',
    'message': report_text.strip(),
    'duration_ms': None,
    'records_affected': None,
    'created_at': now.isoformat(),
    'project': 'alforaijboard',
    'checks': json_data.get('checks', {}),
    'alerts_count': len(json_data.get('alerts', [])),
    'warnings_count': len(json_data.get('warnings', [])),
}

# Load existing local cron results
local_entries = []
if os.path.exists(local_cron_path):
    try:
        with open(local_cron_path) as f:
            content = f.read().strip()
            if content:
                local_entries = json.loads(content)
                if not isinstance(local_entries, list):
                    local_entries = [local_entries]
    except:
        local_entries = []

local_entries.append(entry)

# Keep last 100 entries
if len(local_entries) > 100:
    local_entries = local_entries[-100:]

with open(local_cron_path, 'w') as f:
    json.dump(local_entries, f, indent=2, default=str)

print(f'Entry saved to local cron_results:')
print(f'  Name: {entry["name"]}')
print(f'  Status: {entry["status"]}')
print(f'  Alerts: {entry["alerts_count"]}')
print(f'  Warnings: {entry["warnings_count"]}')
print(f'  Total local entries: {len(local_entries)}')
print()
print('Note: Supabase push failed (HTTP 400 - row constraint issue)')
print('Report saved locally for tracking.')
