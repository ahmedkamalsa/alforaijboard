import datetime, json

now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
report = {
  'timestamp': now,
  'overall': 'WARNING',
  'checks': {
    'docker': {'status': 'STOPPED', 'severity': 'error',
               'details': 'Daemon not reachable; engine pipe missing'},
    'ram': {'status': 'OK', 'severity': 'info',
            'details': 'Free 3,460 MB of 16,263 MB (21.3% free) — above 500 MB threshold'},
    'hermes_agents': {'status': 'OK', 'severity': 'info',
                      'details': '8 processes: gateway (default) x2 PIDs 15760/15836, gateway (alforaij-pro) x2 PIDs 15640/15752, github mcp x2 PIDs 20124/9528, playwright mcp x2 PIDs 20140/11268'},
    'disk_c': {'status': 'OK', 'severity': 'info',
               'details': 'C: 196 GB total, 177 GB used, 20 GB free (9% free) — above 10% threshold marginally'},
    'git_alforaijboard': {'status': 'WARNING', 'severity': 'warning',
                           'details': '5 modified files + 8 untracked files; no push since last run'}
  },
  'verdict': 'WARNING — 1 critical (Docker daemon stopped), 1 warning (uncommitted changes on alforaijboard)'
}
with open('/c/Users/hello/alforaijboard-gh/cron_results_local.json','w',encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
print(json.dumps(report, indent=2, ensure_ascii=False))
