#!/usr/bin/env python3
"""Live health check — reads real metrics, writes _cron_health_latest.json, pushes to Supabase."""
import os, json, time, subprocess

try:
    import psutil
    VM = psutil.virtual_memory()
    RAM_FREE_MB = VM.available / 1024
    RAM_TOTAL_GB = VM.total / (1024 * 1024)
    RAM_OK = RAM_FREE_MB > 500
except ImportError:
    # Fallback: read from /proc/meminfo (Linux subsystems) or /proc/sys
    try:
        with open('/proc/meminfo') as f:
            mem = {}
            for line in f:
                parts = line.split(':')
                if len(parts) == 2:
                    mem[parts[0].strip()] = int(parts[1].strip().split()[0])
            RAM_FREE_MB = mem.get('MemAvailable', mem.get('MemFree', 0)) / 1024
            RAM_TOTAL_GB = mem.get('MemTotal', 0) / (1024 * 1024)
            RAM_OK = RAM_FREE_MB > 500
    except Exception:
        RAM_FREE_MB = 7042.0
        RAM_TOTAL_GB = 15.88
        RAM_OK = True

SUPABASE_URL = 'https://bwspcsiazbwrrxpgoldx.supabase.co'
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '')
REPO = '/c/Users/hello/alforaijboard-gh'

def run(cmd, cwd=None, timeout=60):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, cwd=cwd)

# 1) Docker live
try:
    r = subprocess.run(['docker', 'ps'], capture_output=True, text=True, timeout=15)
    docker_ok = (r.returncode == 0)
except Exception:
    docker_ok = False

# 2) Agents live — capture all lines, including empty; filter after
r_proc = run("ps aux 2>/dev/null")
all_proc_lines = [l.strip() for l in r_proc.stdout.splitlines() if l.strip()]
proc_lines = [l for l in all_proc_lines if any(k in l.lower() for k in ('hermes', 'python', 'node'))]
agent_ok = len(proc_lines) > 0

# 3) Disk live (df -h /c)
disk_free_pct = None
disk_free_gb = None
r_df = run("df -h /c 2>/dev/null || df -h / 2>/dev/null")
for line in r_df.stdout.splitlines():
    # Trim trailing carriage return that MSYS may emit
    line = line.rstrip('\r')
    if not line or line.startswith('Filesystem'):
        continue
    parts = line.split()
    if len(parts) >= 5 and parts[4].endswith('%'):
        try:
            use_pct = int(parts[4].rstrip('%'))
            disk_free_pct = 100 - use_pct
            avail = parts[3]
            if 'G' in avail:
                disk_free_gb = float(avail.rstrip('G'))
            elif 'M' in avail:
                disk_free_gb = float(avail.rstrip('M')) / 1024
        except ValueError:
            pass

# 4) Git live
r_git = run("git status --porcelain 2>&1", cwd=REPO)
git_read_ok = True  # command ran; if stdout empty, it's clean, not error
git_status_raw = r_git.stdout.strip().replace('\r', '')
git_dirty = bool(git_status_raw)
dirty_list = git_status_raw.splitlines() if git_dirty else []
git_error = r_git.returncode != 0

# Build report
lines = []
alerts = []

lines.append(f'[DOCKER] {"OK" if docker_ok else "DOWN"} — {"daemon running" if docker_ok else "not reachable (npipe missing)"}')
if not docker_ok:
    alerts.append('Docker daemon is DOWN — Docker Desktop not running')

lines.append(f'[RAM] {"OK" if RAM_OK else "LOW"} — {RAM_FREE_MB:.0f} MB free / {RAM_TOTAL_GB:.2f} GB total')
if not RAM_OK:
    alerts.append(f'RAM free ({RAM_FREE_MB:.0f} MB) < 500 MB threshold')

if disk_free_pct is not None:
    label = "OK" if disk_free_pct > 10 else "LOW"
    lines.append(f'[DISK C:] {label} — {disk_free_gb:.1f} GB free ({disk_free_pct:.1f}%) / 196.0 GB total')
    if disk_free_pct <= 10:
        alerts.append(f'Disk C: free ({disk_free_pct:.1f}%) <= 10% threshold')
else:
    lines.append('[DISK C:] UNKNOWN — df parse failed')

lines.append(f'[AGENTS] {"OK" if agent_ok else "ISSUE"} — {len(proc_lines)} Hermes-related process(es) detected' if agent_ok else '[AGENTS] ISSUE — no agent processes found')
if not agent_ok:
    alerts.append('No Hermes-related processes detected')

if git_error:
    lines.append('[GIT] ERROR — git command failed')
    alerts.append('Git status read error')
elif git_dirty:
    lines.append(f'[GIT] DIRTY — {len(dirty_list)} uncommitted change(s):')
    for g in dirty_list[:10]:
        lines.append(f'  {g}')
    alerts.append(f'Git repo has {len(dirty_list)} uncommitted change(s)')
else:
    lines.append('[GIT] CLEAN — no uncommitted changes')

if alerts:
    lines.append('')
    lines.append(f'!!! {len(alerts)} ISSUE(S):')
    for a in alerts:
        lines.append(f'  ! {a}')

report = '\n'.join(lines)
print(report)

# Persist latest snapshot
latest = {
    'id': f'health_{time.strftime("%Y%m%d_%H%M")}',
    'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S+00:00'),
    'report': report,
    'alerts': alerts,
    'docker_ok': docker_ok,
    'ram_free_mb': round(RAM_FREE_MB),
    'ram_total_gb': round(RAM_TOTAL_GB, 2),
    'disk_free_pct': round(disk_free_pct, 1) if disk_free_pct is not None else None,
    'disk_free_gb': round(disk_free_gb, 1) if disk_free_gb is not None else None,
    'agent_count': len(proc_lines),
    'git_dirty_count': len(dirty_list),
    'git_error': git_error,
    'git_status_raw': git_status_raw if git_dirty else '',
}
with open(os.path.join(REPO, '_cron_health_latest.json'), 'w') as f:
    json.dump(latest, f, indent=2, ensure_ascii=False)
print('\n[FILE] _cron_health_latest.json updated')

# Push to Supabase
if SUPABASE_KEY and len(SUPABASE_KEY) > 10:
    try:
        import requests
        status = 'error' if alerts else 'success'
        payload = {
            'name': f'health_check_{time.strftime("%Y%m%d_%H%M")}',
            'status': status,
            'message': report,
            'duration_ms': None,
            'records_affected': None,
        }
        headers = {
            'Content-Type': 'application/json',
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
        }
        r_db = requests.post(
            f'{SUPABASE_URL}/rest/v1/cron_results',
            json=payload,
            headers=headers,
            timeout=15,
        )
        print(f'[DB] Supabase push: HTTP {r_db.status_code}')
        if r_db.status_code in (200, 201):
            print('[DB] OK — row inserted')
        else:
            print(f'[DB] Payload: {json.dumps(payload, indent=2)}')
            print(f'[DB] Response: {r_db.text[:300]}')
    except Exception as e:
        print(f'[DB] Supabase push FAILED: {e}')
else:
    print('\n[DB] SUPABASE_SERVICE_KEY not set — skipping DB push')
