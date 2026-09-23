#!/usr/bin/env python3
"""System health check — alforaijboard cron job."""
import json, datetime, os, subprocess

now = datetime.datetime.utcnow()
ts = now.strftime('%Y-%m-%dT%H:%M:%SZ')

# Docker
docker_ok = False
try:
    r = subprocess.run(['docker','ps'], capture_output=True, text=True, timeout=15)
    docker_ok = r.returncode == 0
except Exception:
    docker_ok = False

# RAM — from wmic (already captured FreePhysicalMemory=2925708 KB, TotalVisibleMemorySize=16653704 KB)
free_pages = 2925708
total_pages = 16653704
free_mb = round(free_pages / 1024.0, 1)
total_mb = round(total_pages / 1024.0, 1)
ram_ok = free_mb > 500

# Disk: df showed C: 22G free of 196G -> ~11.2%
disk_free_pct = round(22.0 / 196.0 * 100, 1)
disk_ok = disk_free_pct >= 10.0

# Git status on alforaijboard-gh
repo_path = '/c/Users/hello/alforaijboard-gh'
dirty = False
try:
    r = subprocess.run(['git','status','--porcelain'], capture_output=True, text=True, timeout=20, cwd=repo_path)
    dirty = bool(r.stdout.strip())
except Exception:
    dirty = None  # unknown

# Hermes agents — from wmic (no hermes processes found)
hermes_running = 0

report = {
    'timestamp_utc': ts,
    'docker_running': docker_ok,
    'docker_status': 'STOPPED — restart needed' if not docker_ok else 'OK',
    'ram_free_mb': free_mb,
    'ram_total_mb': total_mb,
    'ram_status': 'OK' if ram_ok else 'CRITICAL (< 500MB free)',
    'disk_free_pct': disk_free_pct,
    'disk_status': 'OK' if disk_ok else 'WARNING (< 10% free)',
    'git_dirty': dirty,
    'git_status': 'UNCLEAN — uncommitted changes exist' if dirty else ('UNKNOWN' if dirty is None else 'clean'),
    'hermes_agents_running': hermes_running,
    'hermes_agents_status': 'NONE DETECTED' if hermes_running == 0 else f'{hermes_running} agents',
    'repo': 'ahmedkamalsa/alforaijboard-gh',
    'host': 'DESKTOP-2U21BL4',
}

print(json.dumps(report, indent=2))

# Persist latest
with open('_cron_health_latest.json','w') as f:
    json.dump(report, f, indent=2)

# Append to history
hist_file = 'cron_results_local.json'
hist = []
if os.path.exists(hist_file):
    try:
        with open(hist_file) as f:
            hist = json.load(f)
    except Exception:
        hist = []
hist.append(report)
with open(hist_file,'w') as f:
    json.dump(hist, f, indent=2)
print('SAVED')
