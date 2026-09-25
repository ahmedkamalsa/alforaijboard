import os
import json
import time
import subprocess
import requests
from datetime import datetime, timezone

SUPABASE_URL = 'https://bwspcsiazbwrrxpgoldx.supabase.co'
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '')

def run(cmd):
    try:
        if isinstance(cmd, str):
            p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30, env=os.environ)
        else:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=30, env=os.environ)
        return p.stdout.strip(), p.stderr.strip(), p.returncode
    except Exception as e:
        return "", str(e), 1

# Cached git status (reuse within same run)
_git_cache = {}

def get_git_status(git_dir):
    if git_dir in _git_cache:
        return _git_cache[git_dir]
    out, err, rc = run('bash -c "cd /c/Users/hello/alforaijboard-gh && git status --porcelain"')
    _git_cache[git_dir] = (out, err, rc)
    return out, err, rc

report_lines = []
alerts = []
warnings = []
timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

# ---------- 1. Docker ----------
docker_status = "UNKNOWN"
docker_containers = []
try:
    out, err, rc = run("docker info --format '{{.ServerVersion}}' 2>&1")
    if rc == 0 and out and "error" not in out.lower():
        docker_status = "running"
        # List containers
        out2, _, rc2 = run("docker ps --format '{{.ID}} {{.Names}} {{.Image}}' 2>&1")
        if rc2 == 0 and out2:
            docker_containers = [l for l in out2.splitlines() if l.strip()]
        report_lines.append(f"[DOCKER] OK — daemon v{out} | {len(docker_containers)} container(s): {', '.join(docker_containers) if docker_containers else 'none running'}")
    else:
        raise Exception(err or out)
except Exception as e:
    docker_status = "DOWN"
    report_lines.append(f"[DOCKER] DOWN — {e}")
    alerts.append("Docker daemon is DOWN — Docker Desktop not running")
    # Attempt restart via net start
    try:
        out3, err3, rc3 = run("net start com.docker.service 2>&1")
        import time; time.sleep(4)
        out4, err4, rc4 = run("docker info --format '{{.ServerVersion}}' 2>&1")
        if rc4 == 0 and out4:
            docker_status = "RESTARTED"
            report_lines[-1] = f"[DOCKER] RESTARTED — daemon v{out4}"
            alerts[-1] = "Docker daemon was DOWN, restarted successfully"
            # Re-list containers
            out5, _, rc5 = run("docker ps --format '{{.ID}} {{.Names}} {{.Image}}' 2>&1")
            if rc5 == 0 and out5:
                docker_containers = [l for l in out5.splitlines() if l.strip()]
            report_lines.append(f"  Containers: {', '.join(docker_containers) if docker_containers else 'none'}")
        else:
            report_lines.append(f"  Restart FAILED — manual intervention required")
            alerts.append("Docker restart failed — manual intervention required")
    except Exception as restart_err:
        report_lines.append(f"  Restart FAILED: {restart_err}")
        alerts.append(f"Docker restart failed: {restart_err}")

# ---------- 2. RAM (WMIC) ----------
ram_free_mb = None
ram_total_gb = None
try:
    out, err, rc = run("wmic os get FreePhysicalMemory,TotalVisibleMemorySize /Value 2>&1")
    free_kb = total_kb = None
    for line in out.splitlines():
        if line.startswith("FreePhysicalMemory="):
            try: free_kb = int(line.split("=")[1])
            except: pass
        if line.startswith("TotalVisibleMemorySize="):
            try: total_kb = int(line.split("=")[1])
            except: pass
    if free_kb and total_kb:
        ram_free_mb = round(free_kb / 1024, 1)
        ram_total_gb = round(total_kb / (1024*1024), 2)
        status = "OK" if ram_free_mb > 500 else "LOW"
        report_lines.append(f"[RAM] {status} — {ram_free_mb:.0f} MB free / {ram_total_gb} GB total")
        if ram_free_mb <= 500:
            alerts.append(f"RAM free ({ram_free_mb:.0f} MB) <= 500 MB threshold")
    else:
        raise Exception("Could not parse WMIC output")
except Exception as e:
    # Fallback: PowerShell
    try:
        out2, _, _ = run("powershell -Command \"$m=(Get-CimInstance Win32_OperatingSystem); '{0} {1}' -f $m.FreePhysicalMemory, $m.TotalVisibleMemorySize\" 2>&1")
        parts = out2.split()
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            ram_free_mb = round(int(parts[0]) / 1024, 1)
            ram_total_gb = round(int(parts[1]) / (1024*1024), 2)
            status = "OK" if ram_free_mb > 500 else "LOW"
            report_lines.append(f"[RAM] {status} — {ram_free_mb:.0f} MB free / {ram_total_gb} GB total")
            if ram_free_mb <= 500:
                alerts.append(f"RAM free ({ram_free_mb:.0f} MB) <= 500 MB threshold")
        else:
            raise Exception("PS parse failed")
    except Exception as e2:
        report_lines.append(f"[RAM] ERROR — {e2}")
        alerts.append(f"RAM check failed: {e2}")

# ---------- 3. Hermes agents (tasklist) ----------
agent_count = 0
agent_procs = []
try:
    out, err, rc = run("tasklist /FO CSV /NH 2>&1")
    for line in out.splitlines():
        low = line.lower()
        if any(x in low for x in ["hermes", "python", "node", "uv", "npm", "git", "docker"]):
            agent_count += 1
            if len(agent_procs) < 10:
                agent_procs.append(line)
    if agent_count > 0:
        report_lines.append(f"[AGENTS] OK — {agent_count} relevant process(es) found")
        for p in agent_procs[:5]:
            report_lines.append(f"  {p}")
    else:
        report_lines.append("[AGENTS] None detected — verify Hermes is running")
        alerts.append("No Hermes/agent-related processes found")
except Exception as e:
    report_lines.append(f"[AGENTS] ERROR — {e}")
    alerts.append(f"Agent check failed: {e}")

# ---------- 4. Disk C: (WMIC) ----------
disk_free_gb = None
disk_total_gb = None
disk_free_pct = None
try:
    out, err, rc = run("wmic logicaldisk get size,freespace,caption /Value 2>&1")
    free_bytes = total_bytes = None
    current = None
    for line in out.splitlines():
        if line.startswith("Caption="):
            current = line.split("=")[1].strip()
        if line.startswith("FreeSpace=") and current == "C:":
            try: free_bytes = int(line.split("=")[1])
            except: pass
        if line.startswith("Size=") and current == "C:":
            try: total_bytes = int(line.split("=")[1])
            except: pass
    if free_bytes and total_bytes:
        disk_free_gb = round(free_bytes / (1024**3), 2)
        disk_total_gb = round(total_bytes / (1024**3), 2)
        disk_free_pct = round((free_bytes / total_bytes) * 100, 1)
        status = "OK" if disk_free_pct > 10 else ("LOW" if disk_free_pct > 5 else "CRITICAL")
        report_lines.append(f"[DISK C:] {status} — {disk_free_gb} GB free ({disk_free_pct}%) / {disk_total_gb} GB total")
        if disk_free_pct <= 10:
            alerts.append(f"Disk C: free space ({disk_free_pct}%) <= 10% threshold")
    else:
        raise Exception("Could not parse WMIC disk output")
except Exception as e:
    report_lines.append(f"[DISK] ERROR — {e}")
    alerts.append(f"Disk check failed: {e}")

# ---------- 5. Git alforaijboard ----------
# Use MSYS git directly (bash 'git' wraps to Windows git which can fail in subprocess)
git_dir = "/c/Users/hello/alforaijboard-gh"
git_dirty = []
try:
    out, err, rc = get_git_status(git_dir)
    if rc == 0:
        git_dirty = [l for l in out.splitlines() if l.strip()]
        if git_dirty:
            report_lines.append(f"[GIT] DIRTY — {len(git_dirty)} uncommitted change(s):")
            for g in git_dirty[:10]:
                report_lines.append(f"  {g}")
            if len(git_dirty) > 10:
                report_lines.append(f"  ... and {len(git_dirty) - 10} more")
            alerts.append(f"Git repo has {len(git_dirty)} uncommitted change(s)")
        else:
            report_lines.append("[GIT] CLEAN — no uncommitted changes")
    else:
        # Fallback: reuse cached result
        out2, err2, rc2 = get_git_status(git_dir)
        if rc2 == 0 and out2.strip():
            git_dirty = [l for l in out2.splitlines() if l.strip()]
            report_lines.append(f"[GIT] DIRTY ({len(git_dirty)} changes, fallback shell) — first 5:")
            for g in git_dirty[:5]:
                report_lines.append(f"  {g}")
            alerts.append(f"Git repo has {len(git_dirty)} uncommitted change(s) [fallback]")
        elif rc2 == 0:
            report_lines.append("[GIT] CLEAN — no uncommitted changes")
        else:
            raise Exception(f"git failed (list+fallback): {err or err2}")
except Exception as e:
    report_lines.append(f"[GIT] ERROR — {e}")
    alerts.append(f"Git check failed: {e}")

# ---------- Summary ----------
report_lines.append("")
if alerts:
    report_lines.append(f"!!! {len(alerts)} ISSUE(S):")
    for a in alerts:
        report_lines.append(f"  ! {a}")
    overall = "warning"
else:
    report_lines.append("All systems nominal.")
    overall = "success"

report_text = "\n".join(report_lines)
print(report_text)

# ---------- Supabase push ----------
if SUPABASE_KEY and len(SUPABASE_KEY) > 10:
    payload = {
        'name': f'health_check_{datetime.now().strftime("%Y%m%d_%H%M")}',
        'status': 'error',
        'message': report_text,
        'duration_ms': None,
        'records_affected': None,
    }
    headers = {
        'Content-Type': 'application/json',
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
    }
    try:
        resp = requests.post(
            f'{SUPABASE_URL}/rest/v1/cron_results',
            json=payload,
            headers=headers,
            timeout=15,
        )
        print(f'\n[DB] Supabase push: HTTP {resp.status_code}')
        if not (resp.status_code == 200 or resp.status_code == 201):
            print(f'[DB] Payload: {json.dumps(payload, indent=2)}')
            print(f'[DB] Response: {resp.text[:500]}')
    except requests.exceptions.RequestException as e:
        print(f'\n[DB] HTTP error: {e}')
    except Exception as e:
        print(f'\n[DB] Supabase push FAILED: {e}')
else:
    print('\n[DB] SUPABASE_SERVICE_KEY not set — skipping DB push')
