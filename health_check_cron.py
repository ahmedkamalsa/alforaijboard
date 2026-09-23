#!/usr/bin/env python3
"""Final health check - writes to cwd since scratch dir has MSYS path issues."""
import subprocess, os, datetime, json
import psutil

def run(cmd, timeout=30):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, '', 'timeout'

now = datetime.datetime.now(datetime.UTC)
report_lines = []
alerts = []
warnings = []
json_result = {
    'timestamp': now.isoformat(),
    'checks': {},
    'alerts': [],
    'warnings': [],
}

# 1. Docker
rc, out, err = run('docker ps --format "{{.Names}}"')
if rc == 0:
    containers = [c.strip() for c in out.splitlines() if c.strip()]
    status = 'ok'
    detail = f'{len(containers)} container(s): {", ".join(containers) if containers else "none running"}'
    if not containers:
        warnings.append('Docker daemon running but no containers')
else:
    status = 'down'
    detail = 'Docker daemon not running'
    alerts.append('Docker daemon is DOWN - Docker Desktop may need to be started')
json_result['checks']['docker'] = {'status': status, 'detail': detail}

report_lines.append(f'[DOCKER] {"OK" if status == "ok" else "DOWN"} - {detail}')

# 2. RAM
try:
    mem = psutil.virtual_memory()
    free_mb = mem.available / (1024*1024)
    total_gb = mem.total / (1024*1024*1024)
    status = 'ok' if free_mb > 500 else 'low'
    detail = f'{free_mb:.0f} MB free / {total_gb:.2f} GB total'
    if free_mb <= 500:
        alerts.append(f'Low RAM: {free_mb:.0f} MB free (threshold: 500 MB)')
except Exception as e:
    status = 'error'
    detail = str(e)
    alerts.append(f'RAM check failed: {e}')
json_result['checks']['ram'] = {'status': status, 'detail': detail}

report_lines.append(f'[RAM] {"OK" if status == "ok" else "LOW" if status == "low" else "ERROR"} - {detail}')

# 3. Hermes agents
hermes_procs = []
for p in psutil.process_iter(['pid', 'name', 'memory_info']):
    try:
        info = p.info
        if (info['name'] or '').lower() and 'hermes' in (info['name'] or '').lower():
            hermes_procs.append(info)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        continue

status = 'ok' if hermes_procs else 'none'
detail = f'{len(hermes_procs)} Hermes process(es) running' if hermes_procs else 'No separate Hermes processes (this cron job IS the agent)'
json_result['checks']['agents'] = {'status': status, 'detail': detail}

report_lines.append(f'[AGENTS] {"OK" if status == "ok" else "INFO"} - {detail}')

# 4. Disk
try:
    usage = psutil.disk_usage('C:\\\\')
    free_gb = usage.free / (1024*1024*1024)
    total_gb = usage.total / (1024*1024*1024)
    free_pct = (usage.free / usage.total) * 100
    status = 'ok' if free_pct > 10 else ('low' if free_pct > 5 else 'critical')
    detail = f'{free_gb:.2f} GB free ({free_pct:.1f}%) / {total_gb:.2f} GB total'
    if free_pct <= 10:
        alerts.append(f'Low disk space: {free_pct:.1f}% free on C: (threshold: 10%)')
except Exception as e:
    status = 'error'
    detail = str(e)
    alerts.append(f'Disk check failed: {e}')
json_result['checks']['disk'] = {'status': status, 'detail': detail}

report_lines.append(f'[DISK C:] {"OK" if status == "ok" else "LOW" if status == "low" else "CRITICAL" if status == "critical" else "ERROR"} - {detail}')

# 5. Git
repo_win = 'C:\\\\Users\\\\hello\\\\alforaijboard-gh'
git_dirty = []
git_error = None

if os.path.isdir(os.path.join(repo_win, '.git')):
    env = os.environ.copy()
    env['GIT_DIR'] = os.path.join(repo_win, '.git')
    env['GIT_WORK_TREE'] = repo_win
    try:
        r = subprocess.run(['git', 'status', '--porcelain'],
                          capture_output=True, text=True, timeout=30, env=env, cwd=repo_win)
        if r.returncode == 0:
            git_dirty = [l.strip() for l in r.stdout.splitlines() if l.strip()]
        else:
            git_error = r.stderr.strip()
    except Exception as e:
        git_error = str(e)

if git_dirty and not git_error:
    status = 'dirty'
    modified = [d for d in git_dirty if d.startswith('M ') or d.startswith('MM ')]
    untracked = [d for d in git_dirty if d.startswith('?? ')]
    deleted = [d for d in git_dirty if d.startswith('D ')]
    detail = f'{len(git_dirty)} changes: {len(modified)} modified, {len(untracked)} untracked'
    if deleted:
        detail += f', {len(deleted)} deleted'
    alerts.append(f'Git repo has uncommitted changes: {detail}')
elif git_error:
    status = 'error'
    detail = git_error
    alerts.append('Git check failed')
else:
    status = 'clean'
    detail = 'No uncommitted changes'
json_result['checks']['git'] = {'status': status, 'detail': detail, 'dirty_count': len(git_dirty)}

report_lines.append(f'[GIT] {"DIRTY" if status == "dirty" else "CLEAN" if status == "clean" else "ERROR"} - {detail}')

# Build the report
report_lines.append('')
if alerts:
    report_lines.append(f'!!! HEALTH ALERTS ({len(alerts)}):')
    for a in alerts:
        report_lines.append(f'  ⚠ {a}')
else:
    report_lines.append('✓ All systems nominal')

if warnings:
    report_lines.append('')
    report_lines.append(f'~ Minor notes ({len(warnings)}):')
    for w in warnings:
        report_lines.append(f'  ⋅ {w}')

report = '\n'.join(report_lines)
print(report)

# Write files to current working directory (avoids MSYS path issues)
cwd = os.getcwd()
# Use forward slashes for the file path since we're on MSYS
report_path = os.path.join(cwd, 'health_report.txt')
json_path = os.path.join(cwd, 'health_report.json')

# If that fails, try the scratch dir with Windows path
if not os.path.exists(cwd):
    # Fallback to Windows path
    appdata = os.environ.get('LOCALAPPDATA', 'C:\\Users\\hello\\AppData\\Local')
    scratch = os.path.join(appdata, 'hermes', 'cache', 'scratch')
    os.makedirs(scratch, exist_ok=True)
    report_path = os.path.join(scratch, 'health_report.txt')
    json_path = os.path.join(scratch, 'health_report.json')

with open(report_path, 'w') as f:
    f.write(report)

json_result['alerts'] = alerts
json_result['warnings'] = warnings
json_result['summary'] = 'ALERTS' if alerts else 'OK'

with open(json_path, 'w') as f:
    json.dump(json_result, f, indent=2)

print(f'\n---FILES WRITTEN---')
print(f'  {report_path}')
print(f'  {json_path}')
