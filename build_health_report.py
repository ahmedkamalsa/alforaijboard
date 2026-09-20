#!/usr/bin/env python3
"""Build and save this hour's health report. Pure stdlib. Saves to _cron_health_latest.json AND cron_results_local.json."""
import json, datetime, subprocess, os

BASE = "/c/Users/hello/alforaijboard-gh"
REPORT_FILE = os.path.join(BASE, "cron_results_latest.json")
LOCAL_HISTORY = os.path.join(BASE, "cron_results_local.json")

now_utc = datetime.datetime.now(datetime.timezone.utc)
ts = now_utc.isoformat()
ts_kt = now_utc.astimezone(datetime.timezone(datetime.timedelta(hours=3))).strftime("%Y-%m-%d %H:%M UTC+03:00")
file_ts = now_utc.strftime("%Y%m%d_%H%M")

def run(cmd, timeout=15):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout or ""), (r.stderr or "")
    except Exception as e:
        return -1, "", str(e)

def wmic_kv(cmd):
    rc, out, err = run(cmd)
    d = {}
    if rc == 0:
        for line in out.splitlines():
            line = line.strip()
            if "=" in line and line:
                k, v = line.split("=", 1)
                try:
                    d[k.strip()] = int(v.strip())
                except:
                    d[k.strip()] = v.strip()
    return d

checks = {}

# 1) Docker
rc, out, err = run("docker ps 2>&1", timeout=10)
docker_running = (rc == 0)
checks["docker"] = {
    "status": "RUNNING" if docker_running else "STOPPED",
    "severity": "info" if docker_running else "error",
    "details": ("Docker Desktop daemon running. Containers: " +
                (out.strip().splitlines()[0] if out.strip() else "none"))
                if docker_running
                else f"Docker Desktop daemon not reachable — {err.strip()[:200]}"
}

# 2) RAM
mem = wmic_kv("wmic OS get FreePhysicalMemory,TotalVisibleMemorySize /value")
free_mb = mem.get("FreePhysicalMemory", 0) / 1024.0
total_mb = mem.get("TotalVisibleMemorySize", 0) / 1024.0
pct = (free_mb / total_mb * 100) if total_mb else 0
checks["ram"] = {
    "status": "OK" if free_mb > 500 else "LOW",
    "severity": "info" if free_mb > 500 else "warning",
    "details": f"{free_mb:.1f} MB free / {total_mb:.1f} MB total ({pct:.1f}%) — threshold: 500 MB"
}

# 3) Agents — tasklist + wmic cross-check (different token/credentials)
pids = []

# tasklist (primary — NT AUTHORITY\SYSTEM token)
rc, out_tl, err = run("tasklist /FI \"IMAGENAME eq python.exe\" /NH 2>/dev/null", timeout=10)
for line in out_tl.splitlines():
    parts = line.split()
    if len(parts) >= 2 and parts[0].lower().endswith("python.exe"):
        try: pids.append(int(parts[1]))
        except: pass
rc2, out_node, err2 = run("tasklist /FI \"IMAGENAME eq node.exe\" /NH 2>/dev/null", timeout=10)
for line in out_node.splitlines():
    parts = line.split()
    if len(parts) >= 2 and parts[0].lower().endswith("node.exe"):
        try: pids.append(int(parts[1]))
        except: pass

# wmic cross-check
rc3, out_wmic, err3 = run("wmic process where 'name=\"python.exe\"' get Name,ProcessId /value 2>/dev/null", timeout=10)
for line in out_wmic.splitlines():
    line = line.strip()
    if line == "Name=python.exe":
        cur = "proc"
    elif line.startswith("ProcessId=") and cur == "proc":
        try: pids.append(int(line.split("=")[1]))
        except: pass
        cur = None
rc4, out_nm, err4 = run("wmic process where 'name=\"node.exe\"' get Name,ProcessId /value 2>/dev/null", timeout=10)
cur = None
for line in out_nm.splitlines():
    line = line.strip()
    if line == "Name=node.exe":
        cur = "proc"
    elif line.startswith("ProcessId=") and cur == "proc":
        try: pids.append(int(line.split("=")[1]))
        except: pass
        cur = None

# Dedup PIDs
seen = set()
pids_deduped = []
for p in pids:
    if p not in seen:
        seen.add(p)
        pids_deduped.append(p)

agent_count = len(pids_deduped)
checks["agents"] = {
    "status": "OK" if agent_count > 0 else "NONE",
    "severity": "info" if agent_count > 0 else "warning",
    "details": (f"{agent_count} Hermes-related processes running (PIDs: {','.join(str(p) for p in pids_deduped[:10])})"
                if agent_count > 0
                else "No python/node processes found — Hermes infrastructure may be down")
}

# 4) Disk
rc, out, err = run("df -h /c/Users/hello", timeout=10)
disk_free_gb = disk_total_gb = disk_free_pct = 0.0
disk_used_pct = 100.0
disk_raw = out.strip()
for line in out.splitlines():
    if line.startswith("C:"):
        parts = line.split()
        if len(parts) >= 5:
            disk_total_gb = float(parts[1].replace("G",""))
            disk_free_gb = float(parts[3].replace("G",""))
            disk_used_pct = float(parts[4].replace("%",""))
            disk_free_pct = round(100 - disk_used_pct, 1)
            break
checks["disk"] = {
    "status": "OK" if disk_free_pct >= 10 else "WARNING",
    "severity": "info" if disk_free_pct >= 10 else "warning",
    "details": (f"{disk_free_gb:.0f} GB free / {disk_total_gb:.0f} GB total ({disk_free_pct:.1f}% free)"
                f" — threshold: 10% free; {disk_free_pct:.1f}% {'ABOVE' if disk_free_pct>=10 else 'BELOW'} threshold")
}

# 5) Git
rc, out, err = run("cd C:/Users/hello/alforaijboard-gh && git status --short 2>&1", timeout=10)
modified = []
untracked = 0
if rc == 0:
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("??"):
            untracked += 1
        else:
            modified.append(line[3:] if len(line) > 3 else line)
git_status = "CLEAN" if not modified and not untracked else "DIRTY"
checks["git"] = {
    "status": git_status,
    "severity": "info" if git_status == "CLEAN" else "warning",
    "details": (f"Modified: {', '.join(modified) if modified else 'none'}. "
                f"Untracked: {untracked} file(s)"
                + (f" — commit or stash before pushing" if git_status == "DIRTY" else ""))
}

# Overall
severities = [c["severity"] for c in checks.values()]
if "error" in severities:
    overall = "CRITICAL"
elif "warning" in severities:
    overall = "NEEDS_ATTENTION"
else:
    overall = "HEALTHY"

alerts = [k for k, v in checks.items() if v["severity"] == "error"]
warnings = [k for k, v in checks.items() if v["severity"] == "warning"]

report = {
    "timestamp": ts,
    "timestamp_kt": ts_kt,
    "overall": overall,
    "status": "healthy" if overall == "HEALTHY" else ("degraded" if overall == "NEEDS_ATTENTION" else "down"),
    "checks": checks,
    "alerts": alerts,
    "warnings": warnings,
    "host": "DESKTOP-2U21BL4",
    "docker_status": checks["docker"]["status"],
    "ram_free_mb": round(free_mb, 1),
    "ram_total_mb": round(total_mb, 1),
    "disk_free_gb": round(disk_free_gb, 1),
    "disk_total_gb": round(disk_total_gb, 1),
    "disk_free_pct": disk_free_pct,
    "agent_count": agent_count,
    "agent_pids": pids[:10],
    "git_modified": ", ".join(modified) if modified else "",
    "git_untracked_count": untracked,
    "git_status": git_status,
    "details": json.dumps(checks, ensure_ascii=False)
}

# Save report
with open(REPORT_FILE, "w") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
print(f"Report saved: {REPORT_FILE}")

# Append to local history
new_entry = {
    "cron_id": f"cron_health_{file_ts}",
    "host": "DESKTOP-2U21BL4",
    "timestamp": ts,
    "overall": overall,
    "checks": checks,
    "docker_status": checks["docker"]["status"],
    "ram_free_mb": round(free_mb, 1),
    "ram_total_mb": round(total_mb, 1),
    "disk_free_gb": round(disk_free_gb, 1),
    "disk_total_gb": round(disk_total_gb, 1),
    "disk_free_pct": disk_free_pct,
    "agent_count": agent_count,
    "agent_pids": pids[:10],
    "git_modified": ", ".join(modified) if modified else "",
    "git_untracked_count": untracked,
    "git_status": git_status,
    "details": json.dumps(checks, ensure_ascii=False)
}

history = []
try:
    with open(LOCAL_HISTORY) as f:
        history = json.load(f)
except Exception:
    pass

if not any(e.get("cron_id") == new_entry["cron_id"] for e in history):
    history.append(new_entry)
    with open(LOCAL_HISTORY, "w") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    print(f"Appended to local history: cron_results_local.json — total entries: {len(history)}")

# Print summary
print(f"\n{'='*60}")
print(f"HEALTH REPORT — {ts_kt}")
print(f"Host: DESKTOP-2U21BL4 | Overall: {overall}")
print(f"{'='*60}")
for k, v in checks.items():
    icon = {"RUNNING":"✓","STOPPED":"✗","OK":"✓","LOW":"⚠","WARNING":"⚠","CLEAN":"✓","DIRTY":"⚠","NONE":"✗"}.get(v["status"], "?")
    print(f"  [{icon}] {k.upper()}: {v['status']} — {v['details']}")
print(f"{'='*60}")
if alerts:
    print(f"ALERTS ({len(alerts)}) — needs attention NOW:")
    for a in alerts:
        print(f"  ✗ {a.upper()}")
if warnings:
    print(f"WARNINGS ({len(warnings)}):")
    for w in warnings:
        print(f"  ⚠ {w.upper()}")
print()
print(f"Local history: {LOCAL_HISTORY} — {len(history)} entries saved")
