#!/usr/bin/env python3
"""Hourly system health check - Windows host. Saves local JSON + pushes to Supabase."""
import os, json, datetime, subprocess, shutil
from pathlib import Path

PROJECT_ID = "bwspcsiazbwrrxpgoldx"
SUPABASE_URL = "https://bwspcsiazbwrrxpgoldx.supabase.co"
RESULTS_DIR = Path(r"/c/Users/hello/alforaijboard-gh/cron_results")
LOCAL_HISTORY = Path(r"/c/Users/hello/alforaijboard-gh/cron_results_local.json")
ALFORAIJ_DIR = Path(r"/c/Users/hello/alforaijboard-gh")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

now = datetime.datetime.now(datetime.timezone.utc)
ts = now.isoformat()
file_ts = now.strftime("%Y%m%d_%H%M")

report = {"timestamp": ts, "file_ts": file_ts, "checks": {}}
alerts = []
warnings = []

def run(cmd, timeout=20):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout or "").strip(), (r.stderr or "").strip()
    except Exception as e:
        return -1, "", str(e)

def add_check(name, status, details, severity="info"):
    report["checks"][name] = {"status": status, "severity": severity, "details": details}
    return status, details

# --- 1. Docker daemon ---
rc, out, err = run("docker ps --format '{{.Names}}'")
if rc == 0 and out:
    containers = [c for c in out.split("\n") if c.strip()]
    status, details = add_check("docker",
        "RUNNING",
        f"Docker Desktop daemon running. {len(containers)} container(s): {', '.join(containers) if containers else 'none'}")
    if not containers:
        warnings.append("No containers running (daemon OK)")
elif rc == 0:
    status, details = add_check("docker", "RUNNING", "Docker Desktop daemon running. 0 containers.")
    warnings.append("No containers running (daemon OK)")
else:
    status, details = add_check("docker", "NOT_RUNNING",
        f"Docker daemon down: {err[:200] if err else 'npipe unavailable'}")
    alerts.append(f"DOCKER DOWN — {details}")
    # Attempt restart via service
    rc2, out2, err2 = run("sc start Docker Desktop", timeout=15)
    if rc2 == 0:
        import time; time.sleep(8)
        rc3, out3, err3 = run("docker ps --format '{{.Names}}'")
        if rc3 == 0 and out3:
            add_check("docker", "RESTARTED", f"Restarted: {out3.strip()}")
            alerts[-1] = alerts[-1].replace("DOWN", "DOWN → RESTARTED")
        else:
            add_check("docker_restart", "FAILED", f"Restart attempt failed: {err3[:200]}")
    else:
        add_check("docker_restart", "FAILED", f"Restart not attempted (sc start failed): {err2[:200]}")

# --- 2. RAM ---
rc, out, err = run("wmic OS get FreePhysicalMemory,TotalVisibleMemorySize /value")
free_kb = total_kb = 0
for line in out.splitlines():
    if "FreePhysicalMemory=" in line:
        try: free_kb = int(line.split("=")[1].strip())
        except: pass
    if "TotalVisibleMemorySize=" in line:
        try: total_kb = int(line.split("=")[1].strip())
        except: pass
free_mb = free_kb / 1024.0
total_mb = total_kb / 1024.0
ram_pct = round(free_mb / total_mb * 100, 1) if total_mb else 0
ram_status = "OK" if free_mb > 500 else "LOW"
status, details = add_check("ram", ram_status,
    f"{round(free_mb,1)} MB free / {round(total_mb,1)} MB total ({ram_pct}% free) — threshold: 500 MB")
if ram_status == "LOW":
    alerts.append(f"RAM LOW — {round(free_mb,0)} MB free (≤ 500 MB threshold)")

# --- 3. CPU load ---
rc, out, err = run("wmic cpu get loadpercentage")
load = 0
for line in out.splitlines():
    s = line.strip()
    if s.isdigit():
        load = int(s)
status, details = add_check("cpu", "OK",
    f"CPU load: {load}% | cron runs in isolated shell — Hermes agents tracked separately")

# --- 4. Hermes agents (process scan) ---
rc, out, err = run("powershell -NoProfile -Command \"Get-CimInstance Win32_Process | Where-Object {$_.CommandLine -match 'hermes|agent|workflows' -or $_.Name -match '^hermes'} | Select-Object ProcessId,Name,CommandLine | ConvertTo-Json -Compress\"", timeout=15)
agent_procs = []
if rc == 0 and out:
    try:
        agent_procs = json.loads(out)
    except:
        agent_procs = []
if not agent_procs:
    # fallback: wmic
    rc, out, err = run("wmic process where 'name like \"%hermes%\" or name like \"%node%\" or name like \"%python%\"' get ProcessId,Name,CommandLine /format:csv 2>&1 | head -20", timeout=15)
    for line in out.splitlines()[1:]:
        parts = line.split(",")
        if len(parts) >= 2:
            agent_procs.append({"ProcessId": parts[1].strip(), "Name": parts[2].strip() if len(parts) > 2 else "", "CommandLine": parts[3].strip() if len(parts) > 3 else ""})
agent_count = len(agent_procs)
pids = ", ".join(str(p.get("ProcessId","?")) for p in agent_procs[:10])
agent_status = "OK" if agent_count > 0 else "NONE"
status, details = add_check("hermes_agents", agent_status,
    f"{agent_count} Hermes-related process(es) found. PIDs: {pids if pids else 'none'}")
if agent_status == "NONE":
    alerts.append("No Hermes agent processes detected")

# --- 5. Disk C: ---
rc, out, err = run("powershell -NoProfile -Command \"(Get-CimInstance Win32_LogicalDisk -Filter 'DeviceID=\\\"C:\\\"').FreeSpace / 1GB\"", timeout=15)
free_gb = 0.0
if rc == 0 and out:
    try: free_gb = float(out.strip())
    except: pass
rc, out, err = run("powershell -NoProfile -Command \"(Get-CimInstance Win32_LogicalDisk -Filter 'DeviceID=\\\"C:\\\"').Size / 1GB\"", timeout=15)
total_gb = 0.0
if rc == 0 and out:
    try: total_gb = float(out.strip())
    except: pass
free_pct = round(free_gb / total_gb * 100, 1) if total_gb else 0
used_pct = round(100 - free_pct, 1)
disk_status = "OK" if free_pct > 10 else ("LOW" if free_pct > 5 else "CRITICAL")
status, details = add_check("disk", disk_status,
    f"{round(free_gb,1)} GB free ({free_pct}%) / {round(total_gb,1)} GB total — threshold: 10% free")
if disk_status in ("LOW", "CRITICAL"):
    alerts.append(f"DISK C: LOW — {free_pct}% free (≤ 10% threshold)")
elif free_pct < 15:
    warnings.append(f"Disk C: approaching threshold — {free_pct}% free")

# --- 6. Git alforaijboard ---
rc, out, err = run("cd /c/Users/hello/alforaijboard-gh && git status --porcelain")
lines = [l.strip() for l in out.splitlines() if l.strip()]
modified = [l[3:] for l in lines if l.startswith("M ")]
untracked = [l[3:] for l in lines if l.startswith("?? ")]
git_status = "CLEAN" if not lines else "DIRTY"
status, details = add_check("git", git_status,
    f"{len(modified)} modified, {len(untracked)} untracked" + (f": {', '.join(modified[:5])}{'...' if len(modified)>5 else ''} {', '.join(untracked[:5])}{'...' if len(untracked)>5 else ''}" if lines else ""))
if git_status == "DIRTY":
    alerts.append(f"Git DIRTY — {len(lines)} uncommitted change(s)")
elif lines:
    warnings.append(f"Git has {len(lines)} uncommitted change(s)")

# --- Overall ---
docker_ok = report["checks"]["docker"]["status"] in ("RUNNING", "RESTARTED")
ram_ok = report["checks"]["ram"]["status"] == "OK"
disk_ok = report["checks"]["disk"]["status"] == "OK"
git_ok = report["checks"]["git"]["status"] == "CLEAN"
overall = "HEALTHY" if (docker_ok and ram_ok and disk_ok and git_ok) else "NEEDS_ATTENTION"
report["overall"] = overall

# --- Save local JSON ---
new_entry = {
    "cron_id": f"cron_health_{file_ts}",
    "host": "DESKTOP-2U21BL4",
    "timestamp": ts,
    "overall": overall,
    "docker_status": report["checks"]["docker"]["status"],
    "ram_free_mb": round(free_mb, 1),
    "ram_total_mb": round(total_mb, 1),
    "disk_free_gb": round(free_gb, 1),
    "disk_total_gb": round(total_gb, 1),
    "disk_free_pct": free_pct,
    "cpu_load_pct": load,
    "hermes_agent_count": agent_count,
    "hermes_pids": pids,
    "git_status": git_status,
    "git_modified_count": len(modified),
    "git_untracked_count": len(untracked),
    "git_modified": ", ".join(modified) if modified else "",
    "git_untracked": ", ".join(untracked) if untracked else "",
    "details": json.dumps(report["checks"], ensure_ascii=False),
}
try:
    history = json.loads(LOCAL_HISTORY.read_text()) if LOCAL_HISTORY.exists() else []
except: history = []
if not any(e.get("cron_id") == new_entry["cron_id"] for e in history):
    history.append(new_entry)
LOCAL_HISTORY.write_text(json.dumps(history, indent=2, ensure_ascii=False))

file_out = RESULTS_DIR / f"cron_results_{file_ts}.json"
file_out.write_text(json.dumps(report, indent=2, ensure_ascii=False))

# --- Build readable report ---
report_lines = []
report_lines.append(f"=== SYSTEM HEALTH REPORT — {now.strftime('%Y-%m-%d %H:%M UTC%z')} ===")
report_lines.append(f"Host: DESKTOP-2U21BL4 | Project: {PROJECT_ID} | Cron: cron_health_{file_ts}")
report_lines.append("")
for name in ["docker","ram","cpu","hermes_agents","disk","git"]:
    c = report["checks"][name]
    icon = {"RUNNING":"✓","RESTARTED":"↻","NOT_RUNNING":"✗","OK":"✓","LOW":"⚠","NONE":"✗","CLEAN":"✓","DIRTY":"✗","CRITICAL":"✗"}.get(c["status"],"•")
    report_lines.append(f"[{icon}] {name.upper()}: {c['status']} — {c['details']}")
report_lines.append("")
if alerts:
    report_lines.append(f"!!! {len(alerts)} ALERT(s):")
    for a in alerts:
        report_lines.append(f"  ⚠ {a}")
if warnings:
    report_lines.append(f"~ {len(warnings)} WARNING(s):")
    for w in warnings:
        report_lines.append(f"  ~ {w}")
if not alerts and not warnings:
    report_lines.append("All systems nominal.")
report_lines.append("")
report_lines.append(f"Overall: {overall}")
report_lines.append(f"Local saved: {file_out}")
report_lines.append(f"History: {LOCAL_HISTORY} ({len(history)} entries)")
report_lines.append("")
report_lines.append("[DB] Supabase push status: see below")

report_text = "\n".join(report_lines)
print(report_text)

# --- Push to Supabase (publshable key is READ-ONLY; service key required for INSERT) ---
API_URL = f"{SUPABASE_URL}/rest/v1/cron_results"
ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
if not ANON_KEY:
    ANON_KEY = "sb_publishable_c84oHQS94osRqw_SiTIqMg_8icxvatZ"

row = {
    "timestamp": ts,
    "overall": overall,
    "docker_status": report["checks"]["docker"]["status"],
    "ram_free_mb": round(free_mb, 1),
    "ram_status": report["checks"]["ram"]["status"],
    "disk_free_pct": free_pct,
    "disk_status": report["checks"]["disk"]["status"],
    "git_status": report["checks"]["git"]["status"],
    "details": json.dumps(report["checks"], ensure_ascii=False),
    "name": f"cron_health_{file_ts}",
    "status": "success" if overall == "HEALTHY" else "error",
    "message": report_text,
}

db_status = "SKIPPED (no service key)"
if SERVICE_KEY:
    svc_headers = {"Content-Type": "application/json", "apikey": SERVICE_KEY, "Authorization": f"Bearer {SERVICE_KEY}", "Prefer": "return=minimal"}
    try:
        import urllib.request
        data = json.dumps(row).encode("utf-8")
        req = urllib.request.Request(API_URL, data=data, headers=svc_headers, method="POST")
        with urllib.request.urlopen(req, timeout=15) as resp:
            db_status = f"INSERTED HTTP {resp.status} — {resp.read().decode()[:200]}"
            print(f"\n[DB] Supabase insert: {db_status}")
    except Exception as e:
        db_status = f"FAILED (service key): {e}"
        print(f"\n[DB] Supabase insert failed: {e}")
else:
    db_status = "SKIPPED (no service key)"
print(f"\n[DB] {db_status}")
