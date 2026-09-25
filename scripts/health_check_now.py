import subprocess
import json

now = subprocess.run(["date", "+%Y-%m-%d %H:%M:%S"], capture_output=True, text=True)
timestamp = now.stdout.strip()

checks = {}

# Docker
try:
    r = subprocess.run(["docker", "ps"], capture_output=True, text=True, timeout=10)
    if r.returncode != 0:
        checks["docker"] = {"status": "FAIL", "detail": "Daemon not reachable"}
    else:
        checks["docker"] = {"status": "OK", "detail": "Daemon running"}
except Exception as e:
    checks["docker"] = {"status": "FAIL", "detail": str(e)}

# RAM
try:
    with open("/proc/meminfo") as f:
        lines = f.readlines()
    mem = {}
    for line in lines:
        if "MemTotal" in line or "MemFree" in line:
            k, v = line.split(":", 1)
            mem[k.strip()] = int(v.strip().split()[0])
    total_mb = round(mem.get("MemTotal", 0) / 1024)
    free_mb = round(mem.get("MemFree", 0) / 1024)
    available = free_mb
    if free_mb > 500:
        checks["ram"] = {"status": "OK", "detail": f"Free: {free_mb}MB / Total: {total_mb}MB"}
    else:
        checks["ram"] = {"status": "WARN", "detail": f"Low RAM: {free_mb}MB free"}
except Exception as e:
    checks["ram"] = {"status": "FAIL", "detail": str(e)}

# Disk
try:
    r = subprocess.run(["df", "-m", "C:/Users/hello"], capture_output=True, text=True, timeout=10)
    lines = r.stdout.strip().split("\n")
    if len(lines) >= 2:
        parts = lines[1].split()
        size = int(parts[1])
        used = int(parts[2])
        avail = int(parts[3])
        pct = int(parts[4].replace("%", ""))
        free_room = round((avail / 1024) * 100) / 100
        if pct < 90:
            checks["disk"] = {"status": "OK", "detail": f"Used {pct}% — {free_room}GB free"}
        else:
            checks["disk"] = {"status": "WARN", "detail": f"High usage {pct}% — only {free_room}GB free"}
    else:
        checks["disk"] = {"status": "FAIL", "detail": "Could not parse df output"}
except Exception as e:
    checks["disk"] = {"status": "FAIL", "detail": str(e)}

# Git
try:
    r = subprocess.run(["git", "-C", "C:/Users/hello/alforaijboard-gh", "status", "--short"], capture_output=True, text=True, timeout=10)
    lines = [l for l in r.stdout.strip().split("\n") if l.strip()]
    if lines:
        checks["git"] = {"status": "WARN", "detail": f"{len(lines)} uncommitted changes"}
    else:
        checks["git"] = {"status": "OK", "detail": "Clean working tree"}
except Exception as e:
    checks["git"] = {"status": "FAIL", "detail": str(e)}

# Agents — Hermes process
try:
    r = subprocess.run(["tasklist"], capture_output=True, text=True, timeout=10)
    hermes_lines = [l for l in r.stdout.split("\n") if "hermes" in l.lower()]
    if hermes_lines:
        she = hermes_lines[0]
        checks["agents"] = {"status": "OK", "detail": f"hermes.exe running: {she.strip()}"}
    else:
        checks["agents"] = {"status": "FAIL", "detail": "hermes.exe NOT FOUND in tasklist"}
except Exception as e:
    checks["agents"] = {"status": "FAIL", "detail": str(e)}

report = {
    "timestamp": timestamp,
    "checks": checks,
    "overall": "OK" if all(c.get("status") in ("OK",) for c in checks.values()) else "WARN",
}

print(json.dumps(report, indent=2))
