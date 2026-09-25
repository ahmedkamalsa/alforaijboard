import subprocess
import json
import re
from datetime import datetime, timezone

KWT = timezone.utc  # offset +03:00; will compute local time in report

def run(cmd, timeout=30):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return r.stdout.strip(), r.returncode

stamp_utc, _ = run(["powershell", "-NoProfile", "-Command",
    "Get-Date -Format 'yyyy-MM-dd HH:mm:ss' -Utc"])
stamp_kwt, _ = run(["powershell", "-NoProfile", "-Command",
    "Get-Date -Format 'yyyy-MM-dd HH:mm:ss'"])

# 1) Docker
try:
    out, rc = run(["docker", "ps"], timeout=10)
    docker_status = "RUNNING" if rc == 0 else "STOPPED"
    docker_detail = "Docker Desktop daemon reachable." if rc == 0 else "Docker daemon not reachable (pipe //./pipe/dockerDesktopLinuxEngine missing)."
except Exception as e:
    docker_status = "UNKNOWN"
    docker_detail = str(e)

# 2) RAM
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
        if free_mb > 500:
            ram_status = "OK"
            ram_detail = f"{free_mb} MB free / {total_mb} MB total ({pct_free}% free) — threshold: 500 MB"
        else:
            ram_status = "LOW"
            ram_detail = f"Only {free_mb} MB free — below 500 MB threshold"
    else:
        ram_status = "UNKNOWN"
        ram_detail = "Could not parse RAM info"
except Exception as e:
    ram_status = "UNKNOWN"
    ram_detail = str(e)

# 3) Hermes agent
try:
    out, rc = run(["tasklist"], timeout=10)
    hermes_lines = [l for l in out.splitlines() if "hermes" in l.lower()]
    if hermes_lines:
        pid = re.search(r"\b(\d+)\b", hermes_lines[0])
        pid_str = pid.group(1) if pid else "?"
        agents_status = "OK"
        agents_detail = f"hermes.exe running (PID {pid_str})"
    else:
        agents_status = "NOT_FOUND"
        agents_detail = "hermes.exe not found in process list"
except Exception as e:
    agents_status = "UNKNOWN"
    agents_detail = str(e)

# 4) Disk
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
        if free_pct >= 10:
            disk_status = "OK"
            disk_detail = f"{free_gb} GB free / {total_gb} GB total ({free_pct}% free) — threshold: 10%"
            disk_warn = "no"
        else:
            disk_status = "WARN"
            disk_detail = f"Only {free_gb} GB free ({free_pct}% free) — below 10% threshold"
            disk_warn = "yes"
    else:
        disk_status = "UNKNOWN"
        disk_detail = "Could not parse disk info"
        disk_warn = "no"
except Exception as e:
    disk_status = "UNKNOWN"
    disk_detail = str(e)
    disk_warn = "no"

# 5) Git
try:
    out, rc = run(["git", "-C", "C:/Users/hello/alforaijboard-gh", "status", "--short"], timeout=10)
    lines = [l for l in out.splitlines() if l.strip()]
    modified = sum(1 for l in lines if l[0] in "M AMD" or l.startswith(" M") or " M" in l[:3])
    untracked = sum(1 for l in lines if l.startswith("??"))
    if lines:
        git_status = "UNCLEAN"
        git_detail = f"{len(lines)} changes ({modified} modified, {untracked} untracked)"
    else:
        git_status = "CLEAN"
        git_detail = "No uncommitted changes"
except Exception as e:
    git_status = "UNKNOWN"
    git_detail = str(e)

severity_order = {"OK": 0, "RUNNING": 0, "CLEAN": 0, "STOPPED": 1, "LOW": 1, "WARN": 1,
                  "UNCLEAN": 1, "NOT_FOUND": 2, "UNKNOWN": 3}
statuses = [docker_status, ram_status, agents_status, disk_status, git_status]
max_sev = max(statuses, key=lambda s: severity_order.get(s, 99))
overall = "OK" if max_sev in ("OK", "RUNNING", "CLEAN") else "WARN" if max_sev in ("STOPPED", "LOW", "WARN", "UNCLEAN") else "FAIL"

report = {
    "timestamp": stamp_utc,
    "timestamp_kwt": stamp_kwt,
    "docker": docker_status,
    "ram_total_mb": total_mb if free_kb else None,
    "ram_free_mb": free_mb if free_kb else None,
    "ram_ok": "yes" if ram_status == "OK" else "no",
    "disk_total_gb": total_gb if size_bytes else None,
    "disk_free_gb": free_gb if size_bytes else None,
    "disk_used_pct": used_pct if size_bytes else None,
    "disk_warn": disk_warn,
    "hermes_agents": agents_detail,
    "git_uncommitted": "unclean" if git_status == "UNCLEAN" else "clean",
    "git_modified_count": modified if lines else 0,
    "git_untracked_count": untracked if lines else 0,
    "_local": {
        "docker": docker_status,
        "docker_detail": docker_detail,
        "ram": ram_status,
        "ram_detail": ram_detail,
        "agents": agents_status,
        "agents_detail": agents_detail,
        "disk": disk_status,
        "disk_detail": disk_detail,
        "git": git_status,
        "git_detail": git_detail,
        "overall": overall,
    }
}

print(json.dumps(report, indent=2))
