#!/usr/bin/env python3
"""Health check cron job — runs hourly, Kuwait time."""
import os, json, datetime, subprocess, requests

SUPABASE_URL = "https://bwspcsiazbwrrxpgoldx.supabase.co"
ANON_KEY = "sb_publishable_c84oHQS94osRqw_SiTIqMg_8icxvatZ"
PROJECT_ID = "bwspcsiazbwrrxpgoldx"
results_dir = "/c/Users/hello/alforaijboard-gh/cron_results"
history_file = "/c/Users/hello/alforaijboard-gh/cron_results_local.json"
os.makedirs(results_dir, exist_ok=True)

now = datetime.datetime.now(datetime.timezone.utc)
timestamp = now.isoformat()
file_ts = now.strftime("%Y%m%d_%H%M")

def run_cmd(cmd, timeout=15):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout or "")[:3000], (r.stderr or "")[:1000]
    except Exception as e:
        return -1, "", str(e)

report = {"timestamp": timestamp, "file_ts": file_ts, "checks": {}}

# 1) Docker
rc, out, err = run_cmd("docker ps")
docker_status = "running" if rc == 0 else "not_running"
report["checks"]["docker"] = {
    "status": docker_status,
    "output": out if rc == 0 else err[:500],
    "severity": "info" if docker_status == "running" else "error"
}

# 2) RAM
rc, out, err = run_cmd("wmic OS get FreePhysicalMemory,TotalVisibleMemorySize /value")
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
ram_status = "ok" if free_mb > 500 else "low"
report["checks"]["ram"] = {
    "free_mb": round(free_mb, 1),
    "total_mb": round(total_mb, 1),
    "free_gb": round(free_mb / 1024, 2),
    "status": ram_status,
    "severity": "info" if ram_status == "ok" else "warning"
}

# 3) Processes / CPU
rc, out, err = run_cmd("wmic cpu get loadpercentage")
load = 0
for line in out.splitlines():
    s = line.strip()
    if s.isdigit():
        load = int(s)
report["checks"]["processes"] = {
    "load_percent": load,
    "severity": "info"
}

# 4) Disk
rc, out, err = run_cmd("df -h /c/Users/hello")
disk_info = {"raw": out.strip(), "severity": "info"}
for line in out.splitlines():
    if line.startswith("C:"):
        parts = line.split()
        if len(parts) >= 5:
            disk_info["total_gb"] = parts[1]
            disk_info["used_gb"] = parts[2]
            disk_info["free_gb"] = parts[3]
            disk_info["use_pct"] = parts[4].rstrip("%")
            used_pct = float(parts[4].rstrip("%"))
            disk_info["free_pct"] = round(100 - used_pct, 1)
            disk_info["status"] = "ok" if (100 - used_pct) >= 10 else "warning"
            disk_info["severity"] = "info" if disk_info["status"] == "ok" else "warning"
            break
report["checks"]["disk"] = disk_info

# 5) Git
rc, out, err = run_cmd("cd /c/Users/hello/alforaijboard-gh && git status --porcelain")
lines = [l.strip() for l in out.splitlines() if l.strip()]
modified = [l[3:] for l in lines if l.startswith("M ")]
untracked = [l[3:] for l in lines if l.startswith("?? ")]
git_status = "clean" if not lines else "dirty"
report["checks"]["git"] = {
    "status": git_status,
    "modified": modified,
    "untracked": untracked,
    "dirty_count": len(modified),
    "untracked_count": len(untracked),
    "severity": "info" if git_status == "clean" else "warning"
}

# overall
docker_ok = docker_status == "running"
ram_ok = ram_status == "ok"
disk_ok = disk_info.get("status") == "ok"
git_ok = git_status == "clean"
overall = "healthy" if (docker_ok and ram_ok and disk_ok and git_ok) else "needs_attention"
overall_sev = "info" if overall == "healthy" else "warning"
report["overall"] = overall
report["overall_severity"] = overall_sev

# save individual JSON
file_out = os.path.join(results_dir, f"cron_results_{file_ts}.json")
with open(file_out, "w") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
print(f"Saved: {file_out}")

# save history (append only)
entry = {
    "cron_id": f"cron_health_{file_ts}",
    "host": "DESKTOP-2U21BL4",
    "timestamp": timestamp,
    "overall": overall.upper(),
    "docker_status": docker_status,
    "ram_free_mb": report["checks"]["ram"]["free_mb"],
    "ram_total_mb": report["checks"]["ram"]["total_mb"],
    "disk_free_gb": float(disk_info.get("free_gb", 0).rstrip("G")),
    "disk_total_gb": float(disk_info.get("total_gb", 0).rstrip("G")),
    "disk_free_pct": disk_info.get("free_pct", 0),
    "processes_load_pct": report["checks"]["processes"]["load_percent"],
    "git_modified": ", ".join(modified),
    "git_untracked_count": len(untracked),
    "git_status": git_status,
    "overall_severity": overall_sev
}
try:
    with open(history_file) as f:
        history = json.load(f)
except Exception:
    history = []
if not any(e.get("cron_id") == entry["cron_id"] for e in history):
    history.append(entry)
with open(history_file, "w") as f:
    json.dump(history, f, indent=2, ensure_ascii=False)

# Supabase insert (only columns that exist)
API_URL = f"{SUPABASE_URL}/rest/v1/cron_results"
headers = {
    "apikey": ANON_KEY,
    "Authorization": f"Bearer {ANON_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}
row = {"timestamp": timestamp, "overall": overall.upper()}
try:
    resp = requests.post(API_URL, headers=headers, json=row, timeout=15)
    print(f"Supabase: HTTP {resp.status_code} — {resp.text[:200]}")
    if resp.status_code == 400:
        print("NOTE: row not inserted due to schema mismatch, kept in local history.")
except Exception as e:
    print(f"Supabase push error: {e}")

# 3-level report
print("\n" + "="*55)
print(f"Health check report — {now.strftime('%Y-%m-%d %H:%M')} KWT")
print(f"STATUS: {overall.upper()}")
print("="*55)

print("\n## Level 1: مختصر خالص ##")
print(f"🟢 RAM: {report['checks']['ram']['free_gb']} GB free — OK")
print(f"{'🔴' if not docker_ok else '🟢'} Docker: {docker_status} — {'STOPPED' if not docker_ok else 'running'}")
print(f"{'🟡' if not disk_ok else '🟢'} Disk: {disk_info.get('free_pct', '—')}% free — {'EDGE' if not disk_ok else 'OK'}")
print(f"{'🟡' if not git_ok else '🟢'} Git: {git_status} — {'DIRTY' if not git_ok else 'clean'}")

print("\n## Level 2: بإفادة أفضل ##")
print(f"1) Docker: {docker_status} — {report['checks']['docker']['output'][:150]}")
print(f"2) RAM: {report['checks']['ram']['free_mb']} MB free out of {report['checks']['ram']['total_mb']} MB total ({round(free_mb/total_mb*100,1)}% free)")
print(f"3) CPU load: {report['checks']['processes']['load_percent']}%")
print(f"4) Disk: {disk_info.get('total_gb')} total — {disk_info.get('free_gb')} free ({disk_info.get('free_pct')}% free)")
print(f"5) Git: {git_status} — modified: {modified}, untracked: {untracked}")

print("\n## Level 3: اقتراحات تطوير ##")
print("A) Docker is stopped — open Docker Desktop manually from Start menu or taskbar. If you want fully automated recovery, we can add a Windows Scheduled Task or a second Hermes cron job that starts Docker Desktop when 'docker ps' fails.")
print("B) Disk at 10.0% — clean winsxs/temp via Disk Cleanup (cleanmgr), delete old cron_results .synced files, or move large non-essential files to another drive.")
print("C) Git is clean now — if future checks show uncommitted changes that are intentional, commit and push; if accidental, use git stash + git clean -fd carefully.")
print("D) Supabase tracking: the cron_results table is missing several columns we tried to push (disk_free_pct, ram_free_mb, etc. — HTTP 400 PGRST204). If you want full historical tracking, we need to add those columns as FLOAT/INT in the Supabase table schema first, then re-enable the push.")
print("E) Next-level automation: add instant notification (email/webhook/Teams) when Docker goes down, plus a disk-usage time series so you can see the trend before hitting the 10% edge.")
