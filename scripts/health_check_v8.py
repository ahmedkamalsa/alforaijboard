import subprocess
import json
import re
from datetime import datetime, timezone

def run(cmd, timeout=30):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return r.stdout.strip(), r.returncode

KWT = timezone(offset=0)  # UTC+3 when we subtract from UTC; we'll compute local later

def local_time():
    out, _ = run(["powershell", "-NoProfile", "-Command",
        "Get-Date -Format 'yyyy-MM-dd HH:mm:ss'"])
    return out

stamp_kwt = local_time()

checks = {}

# 1) Docker
try:
    out, rc = run(["docker", "ps"], timeout=10)
    if rc != 0:
        checks["docker_status"] = "STOPPED"
        checks["docker_detail"] = "Docker daemon not reachable (pipe //./pipe/dockerDesktopLinuxEngine missing)."
    else:
        checks["docker_status"] = "RUNNING"
        checks["docker_detail"] = "Docker Desktop daemon reachable."
except Exception as e:
    checks["docker_status"] = "ERROR"
    checks["docker_detail"] = str(e)

# 2) RAM (PowerShell CIM)
try:
    memout, _ = run(["powershell", "-NoProfile", "-Command",
        "Get-CimInstance Win32_OperatingSystem | Select-Object FreePhysicalMemory,TotalVisibleMemorySize | Format-List"])
    free_kb = total_kb = None
    for line in memout.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            v = v.strip()
            if k.strip() == "FreePhysicalMemory":
                free_kb = int(v)
            elif k.strip() == "TotalVisibleMemorySize":
                total_kb = int(v)
    if free_kb is not None and total_kb is not None:
        free_mb = round(free_kb / 1024)
        total_mb = round(total_kb / 1024)
        pct_free = round(free_mb / total_mb * 100, 1)
        checks["ram_total_mb"] = total_mb
        checks["ram_free_mb"] = free_mb
        if free_mb > 500:
            checks["ram_status"] = "OK"
            checks["ram_detail"] = f"{free_mb} MB free / {total_mb} MB total ({pct_free}% free) — threshold: 500 MB"
        else:
            checks["ram_status"] = "LOW"
            checks["ram_detail"] = f"Only {free_mb} MB free — below 500 MB threshold"
    else:
        checks["ram_status"] = "UNKNOWN"
        checks["ram_detail"] = "Could not parse RAM info"
except Exception as e:
    checks["ram_status"] = "ERROR"
    checks["ram_detail"] = str(e)

# 3) Hermes agent process
try:
    out, rc = run(["tasklist"], timeout=10)
    hermes_lines = [l for l in out.splitlines() if "hermes" in l.lower()]
    if hermes_lines:
        pid = re.search(r"\b(\d+)\b", hermes_lines[0])
        pid_str = pid.group(1) if pid else "?"
        checks["agents_status"] = "OK"
        checks["agents_detail"] = f"hermes.exe running (PID {pid_str})"
    else:
        checks["agents_status"] = "NOT_FOUND"
        checks["agents_detail"] = "hermes.exe not found in process list"
except Exception as e:
    checks["agents_status"] = "ERROR"
    checks["agents_detail"] = str(e)

# 4) Disk (PowerShell Get-Volume)
try:
    volout, _ = run(["powershell", "-NoProfile", "-Command",
        "Get-Volume -DriveLetter C | Select-Object SizeRemaining,Size | Format-List"])
    remaining_bytes = size_bytes = None
    for line in volout.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            v = v.strip()
            if k.strip() == "SizeRemaining":
                remaining_bytes = int(v)
            elif k.strip() == "Size":
                size_bytes = int(v)
    if size_bytes and remaining_bytes:
        free_gb = round(remaining_bytes / (1024**3), 2)
        total_gb = round(size_bytes / (1024**3), 2)
        used_pct = round((1 - remaining_bytes / size_bytes) * 100, 1)
        free_pct = round(100 - used_pct, 1)
        checks["disk_total_gb"] = total_gb
        checks["disk_free_gb"] = free_gb
        checks["disk_used_pct"] = used_pct
        if free_pct >= 10:
            checks["disk_status"] = "OK"
            checks["disk_detail"] = f"{free_gb} GB free / {total_gb} GB total ({free_pct}% free) — threshold: 10%"
            checks["disk_warn"] = "no"
        else:
            checks["disk_status"] = "WARN"
            checks["disk_detail"] = f"Only {free_gb} GB free ({free_pct}% free) — below 10% threshold"
            checks["disk_warn"] = "yes"
    else:
        checks["disk_status"] = "UNKNOWN"
        checks["disk_detail"] = "Could not parse disk info"
        checks["disk_warn"] = "no"
except Exception as e:
    checks["disk_status"] = "ERROR"
    checks["disk_detail"] = str(e)
    checks["disk_warn"] = "no"

# 5) Git
try:
    out, rc = run(["git", "-C", "C:/Users/hello/alforaijboard-gh", "status", "--short"], timeout=10)
    lines = [l for l in out.splitlines() if l.strip()]
    modified = sum(1 for l in lines if l[0] in "M AMD" or l.startswith(" M") or " M" in l[:3])
    untracked = sum(1 for l in lines if l.startswith("??"))
    if lines:
        checks["git_status"] = "UNCLEAN"
        checks["git_detail"] = f"{len(lines)} changes ({modified} modified, {untracked} untracked)"
        checks["git_modified_count"] = modified
        checks["git_untracked_count"] = untracked
    else:
        checks["git_status"] = "CLEAN"
        checks["git_detail"] = "No uncommitted changes"
        checks["git_modified_count"] = 0
        checks["git_untracked_count"] = 0
except Exception as e:
    checks["git_status"] = "ERROR"
    checks["git_detail"] = str(e)
    checks["git_modified_count"] = 0
    checks["git_untracked_count"] = 0

# Severity
sev = {
    "docker_status": checks.get("docker_status", "ERROR"),
    "ram_status": checks.get("ram_status", "ERROR"),
    "agents_status": checks.get("agents_status", "ERROR"),
    "disk_status": checks.get("disk_status", "ERROR"),
    "git_status": checks.get("git_status", "ERROR"),
}
order = {"OK": 0, "RUNNING": 0, "CLEAN": 0, "STOPPED": 1, "LOW": 1, "WARN": 1, "UNCLEAN": 1,
         "NOT_FOUND": 2, "ERROR": 3, "UNKNOWN": 3}
max_sev = max(sev.values(), key=lambda s: order.get(s, 99))
overall = "OK" if max_sev in ("OK", "RUNNING", "CLEAN") else "WARN" if max_sev in ("STOPPED", "LOW", "WARN", "UNCLEAN") else "FAIL"

report = {
    "timestamp": stamp_kwt,
    "docker": checks.get("docker_status", "UNKNOWN"),
    "ram_total_mb": checks.get("ram_total_mb"),
    "ram_free_mb": checks.get("ram_free_mb"),
    "ram_ok": "yes" if checks.get("ram_status") == "OK" else "no",
    "disk_total_gb": checks.get("disk_total_gb"),
    "disk_free_gb": checks.get("disk_free_gb"),
    "disk_used_pct": checks.get("disk_used_pct"),
    "disk_warn": checks.get("disk_warn", "no"),
    "hermes_agents": checks.get("agents_detail", ""),
    "git_uncommitted": "unclean" if checks.get("git_status") == "UNCLEAN" else "clean",
    "git_modified_count": checks.get("git_modified_count", 0),
    "git_untracked_count": checks.get("git_untracked_count", 0),
    "_local": {
        "docker_detail": checks.get("docker_detail", ""),
        "ram_detail": checks.get("ram_detail", ""),
        "agents_detail": checks.get("agents_detail", ""),
        "disk_detail": checks.get("disk_detail", ""),
        "git_detail": checks.get("git_detail", ""),
        "overall": overall,
    }
}

with open("C:/Users/hello/alforaijboard-gh/_cron_health_latest.json", "w") as f:
    json.dump(report, f, indent=2)

print(json.dumps(report, indent=2))
