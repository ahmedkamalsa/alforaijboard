#!/usr/bin/env python3
import subprocess, json, datetime, os

now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
host = os.environ.get('COMPUTERNAME', 'DESKTOP-2U21BL4')

# 1. Docker
try:
    docker_out = subprocess.run(['docker','ps'], capture_output=True, text=True, timeout=10)
    docker_ok = docker_out.returncode == 0
except:
    docker_ok = False
docker_status = 'OK' if docker_ok else 'DOWN'

# 2. RAM via wmic
try:
    ram_out = subprocess.run(['wmic','OS','get','FreePhysicalMemory,TotalVisibleMemorySize','/Value'], capture_output=True, text=True, timeout=10).stdout
    ram_lines = {}
    for line in ram_out.splitlines():
        if '=' in line:
            k,v = line.split('=',1)
            ram_lines[k.strip()] = v.strip()
    free_mb = int(ram_lines.get('FreePhysicalMemory','0'))/1024
    total_mb = int(ram_lines.get('TotalVisibleMemorySize','1'))/1024
    ram_free_gb = free_mb/1024
    ram_pct = (free_mb/(total_mb or 1))*100
    ram_status = 'OK' if free_mb > 500 else 'LOW'
except Exception as e:
    free_mb = 0; total_mb = 1; ram_free_gb = 0; ram_pct = 0
    ram_status = 'ERROR: '+str(e)

# 3. Hermes processes
try:
    ps_out = subprocess.run(['tasklist','/FI','IMAGENAME eq Hermes.exe','/FO','CSV','/NH'], capture_output=True, text=True, timeout=10).stdout
    hermes_procs = [l.strip() for l in ps_out.splitlines() if l.strip() and 'Hermes' in l]
    hermes_status = 'RUNNING ('+str(len(hermes_procs))+' proc(s))' if hermes_procs else 'NONE_DETECTED'
except Exception as e:
    hermes_procs = []
    hermes_status = 'ERROR: '+str(e)

# 4. Disk
try:
    df = subprocess.run(['df','-h','/c/Users/hello'], capture_output=True, text=True, timeout=10).stdout
    disk_line = [l for l in df.splitlines() if 'Users/hello' in l]
    disk_status = 'UNKNOWN'
    disk_free_pct = 0
    if disk_line:
        parts = disk_line[0].split()
        used_pct = parts[4].rstrip('%')
        disk_free_pct = 100 - int(used_pct)
        disk_status = 'OK' if disk_free_pct >= 10 else 'LOW'
except Exception as e:
    disk_status = 'ERROR: '+str(e)
    disk_free_pct = 0

# 5. Git
try:
    git = subprocess.run(['git','status','--short'], capture_output=True, text=True, cwd='/c/Users/hello/alforaijboard-gh', timeout=10).stdout
    git_lines = [l for l in git.splitlines() if l.strip()]
    git_status = 'CLEAN' if not git_lines else 'UNCLEAN ('+str(len(git_lines))+' changed file(s))'
except Exception as e:
    git_lines = []
    git_status = 'ERROR: '+str(e)

report = {
    'timestamp': now,
    'host': host,
    'docker': {'status': docker_status, 'detail': 'Daemon not reachable' if docker_status=='DOWN' else 'Running'},
    'ram': {'status': ram_status, 'free_mb': round(free_mb), 'total_mb': round(total_mb), 'free_gb': round(ram_free_gb,1), 'pct_free': round(ram_pct,1)},
    'hermes_agents': {'status': hermes_status, 'procs': hermes_procs},
    'disk': {'path': 'C:/Users/hello', 'status': disk_status, 'free_pct': disk_free_pct},
    'git': {'repo': 'alforaijboard-gh', 'status': git_status, 'changes': git_lines}
}
print(json.dumps(report, ensure_ascii=False, indent=2))

# Save local copy
with open('/c/Users/hello/alforaijboard-gh/_cron_health_latest.json','w') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
