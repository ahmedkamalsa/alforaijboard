import psutil, shutil, subprocess, json, datetime, os, urllib.request

now = datetime.datetime.utcnow()
ts_id = now.strftime('%Y%m%d_%H%M')
ts = now.strftime('%Y-%m-%dT%H:%M:%SZ')

results = {}
alerts = []
info = []

# 1. Docker
try:
    r = subprocess.run(['docker', 'ps', '--format', '{{.Names}}'], capture_output=True, text=True, timeout=10)
    if r.returncode == 0:
        containers = [c.strip() for c in r.stdout.strip().split('\n') if c.strip()]
        results['docker'] = {'status': 'OK', 'containers': containers}
        info.append(f'[DOCKER] OK - {len(containers)} container(s): {", ".join(containers) if containers else "(none)"}')
        if not containers:
            info.append('  (no containers running)')
    else:
        results['docker'] = {'status': 'DOWN', 'error': r.stderr.strip()[:200]}
        alerts.append(f'[DOCKER] DOWN - docker ps failed (exit {r.returncode})')
except Exception as e:
    results['docker'] = {'status': 'DOWN', 'error': str(e)[:200]}
    alerts.append(f'[DOCKER] DOWN - {str(e)[:150]}')

# 2. RAM
try:
    mem = psutil.virtual_memory()
    free_mb = int(mem.free // 1048576)
    total_gb = round(mem.total / (1024**3), 2)
    status = 'OK' if free_mb > 500 else 'LOW'
    results['ram'] = {'status': status, 'free_mb': free_mb, 'total_gb': total_gb}
    info.append(f'[RAM] {status} - {free_mb} MB free / {total_gb} GB total')
    if status == 'LOW':
        alerts.append(f'[RAM] FREE {free_mb}MB <= 500MB threshold')
except Exception as e:
    results['ram'] = {'status': 'ERROR'}
    alerts.append(f'[RAM] ERROR - {str(e)[:100]}')

# 3. Hermes agents
try:
    hermes_procs = []
    for p in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info', 'cpu_percent']):
        try:
            ip = p.info
            cmdline = ' '.join(ip['cmdline'] or [])
            name = ip['name'] or ''
            if 'hermes' in cmdline.lower() or 'hermes' in name.lower():
                hermes_procs.append({
                    'pid': ip['pid'],
                    'name': name,
                    'cpu': round(ip['cpu_percent'] or 0, 1),
                    'ram_mb': round((ip['memory_info'].rss if ip['memory_info'] else 0) / 1048576, 1),
                    'cmdline': cmdline[:120]
                })
        except:
            pass
    results['agents'] = {'status': 'OK' if len(hermes_procs) > 0 else 'NONE', 'count': len(hermes_procs), 'processes': hermes_procs[:5]}
    if hermes_procs:
        pids = ', '.join(str(p['pid']) for p in hermes_procs[:5])
        info.append(f'[AGENTS] OK - {len(hermes_procs)} Hermes process(es) (PIDs: {pids})')
        for p in hermes_procs[:5]:
            info.append(f'  PID={p["pid"]} {p["name"]} CPU={p["cpu"]}% RAM={p["ram_mb"]}MB')
    else:
        alerts.append('[AGENTS] NONE - no Hermes processes')
except Exception as e:
    results['agents'] = {'status': 'ERROR'}
    alerts.append(f'[AGENTS] ERROR - {str(e)[:100]}')

# 4. Disk
try:
    disk = shutil.disk_usage('C:/Users/hello')
    free_gb = int(disk.free // (1024**3))
    total_gb = int(disk.total // (1024**3))
    free_pct = round(100 * disk.free / disk.total, 1)
    if free_pct <= 5:
        status = 'CRITICAL'
    elif free_pct <= 10:
        status = 'LOW'
    else:
        status = 'OK'
    results['disk'] = {'status': status, 'free_gb': free_gb, 'total_gb': total_gb, 'free_pct': free_pct}
    info.append(f'[DISK C:] {status} - {free_gb} GB free ({free_pct}%) / {total_gb} GB total')
    if status == 'CRITICAL':
        alerts.append(f'[DISK] CRITICAL - {free_pct}% free <= 10%')
    elif status == 'LOW':
        alerts.append(f'[DISK] WARNING - {free_pct}% free, below 10%')
except Exception as e:
    results['disk'] = {'status': 'ERROR'}
    alerts.append(f'[DISK] ERROR - {str(e)[:100]}')

# 5. Git
try:
    r = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True, cwd='C:/Users/hello/alforaijboard-gh', timeout=10)
    if r.returncode == 0:
        dirty = [l.strip() for l in r.stdout.strip().split('\n') if l.strip()]
        results['git'] = {'status': 'DIRTY' if dirty else 'CLEAN', 'changes': dirty}
        if dirty:
            info.append(f'[GIT] DIRTY - {len(dirty)} uncommitted change(s):')
            for d in dirty:
                info.append(f'  {d}')
            alerts.append(f'[GIT] {len(dirty)} uncommitted change(s)')
        else:
            info.append('[GIT] CLEAN - no uncommitted changes')
    else:
        results['git'] = {'status': 'ERROR'}
        alerts.append('[GIT] ERROR - git status failed')
except Exception as e:
    results['git'] = {'status': 'ERROR'}
    alerts.append(f'[GIT] ERROR - {str(e)[:100]}')

# Build report
report_lines = [f'=== SYSTEM HEALTH REPORT - {now.strftime("%Y-%m-%d %H:%M")} UTC ===']
report_lines.append('Host: DESKTOP-2U21BL4')
report_lines.append('')
report_lines.extend(info)
report_lines.append('')
if alerts:
    report_lines.append(f'!!! {len(alerts)} ISSUE(S):')
    for a in alerts:
        report_lines.append(f'  ! {a}')
else:
    report_lines.append('All systems nominal.')

report = '\n'.join(report_lines)
print(report)

# Write JSON results
json_path = '/c/Users/hello/alforaijboard-gh/_cron_health_latest.json'
try:
    with open(json_path) as f:
        existing = json.load(f)
    if not isinstance(existing, list):
        existing = []
except Exception:
    existing = []
existing.append({'timestamp': ts, 'results': results, 'alerts': len(alerts)})
max_keep = 100
if len(existing) > max_keep:
    existing = existing[-max_keep:]
with open(json_path, 'w') as f:
    json.dump(existing, f, indent=2, ensure_ascii=False)
print(f'\n[Local JSON updated: {json_path}]')

# --- Supabase push ---
SUPABASE_URL = 'https://bwspcsiazbwrrxpgoldx.supabase.co'
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '') or os.environ.get('SUPABASE_ANON_KEY', '')

if not SUPABASE_KEY:
    env_path = '/c/Users/hello/alforaijboard-gh/.env'
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith('SUPABASE_SERVICE_KEY='):
                    SUPABASE_KEY = line.split('=', 1)[1].strip().strip('"').strip("'")
                    break
                elif line.startswith('SUPABASE_ANON_KEY='):
                    SUPABASE_KEY = line.split('=', 1)[1].strip().strip('"').strip("'")
                    break

if SUPABASE_KEY:
    entry_name = f'health_check_{ts_id}'
    overall = 'error' if alerts else 'success'
    payload = {
        'name': entry_name,
        'status': overall,
        'message': report,
        'duration_ms': None,
        'records_affected': None
    }
    url = f'{SUPABASE_URL}/rest/v1/cron_results'
    headers = {'apikey': SUPABASE_KEY, 'Content-Type': 'application/json', 'Prefer': 'return=minimal'}
    req = urllib.request.Request(url, json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode('utf-8')
            print(f'[Supabase] HTTP {resp.status} - inserted: {entry_name}')
            if body and body != '':
                print(f'  Response: {body[:200]}')
    except Exception as e:
        print(f'[Supabase] Push FAILED: {e}')
else:
    print('[Supabase] Skipped - no key available')
