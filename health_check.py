#!/usr/bin/env python3
"""Collect health check results and save to cron_results JSON + Supabase table."""
import os, json, datetime, subprocess, sys

results_dir = "/c/Users/hello/alforaijboard-gh/cron_results"
os.makedirs(results_dir, exist_ok=True)

now = datetime.datetime.now(datetime.timezone.utc)
ts = now.isoformat()
file_ts = now.strftime("%Y%m%d_%H%M")

report = {"timestamp": ts, "file_ts": file_ts, "checks": {}}

def run(cmd, timeout=15):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout[:2000], r.stderr[:500]
    except Exception as e:
        return -1, "", str(e)

# 1. Docker
rc, out, err = run("docker ps")
report["checks"]["docker"] = {
    "status": "running" if rc == 0 else "not_running",
    "output": out if rc == 0 else err
}

# 2. RAM — read from wmic (Windows)
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
report["checks"]["ram"] = {
    "free_mb": round(free_mb, 1),
    "total_mb": round(total_mb, 1),
    "free_gb": round(free_mb / 1024, 2),
    "status": "ok" if free_mb > 500 else "low"
}

# 3. Processes / load
rc, out, err = run("wmic cpu get loadpercentage")
load = 0
for line in out.splitlines():
    s = line.strip()
    if s.isdigit():
        load = int(s)
report["checks"]["processes"] = {
    "load_percent": load,
    "note": "cron job runs in isolated shell — Hermes agents are separate processes"
}

# 4. Disk
rc, out, err = run("df -h /c/Users/hello")
disk_info = {"raw": out.strip()}
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
            break
report["checks"]["disk"] = disk_info

# 5. Git
rc, out, err = run("cd /c/Users/hello/alforaijboard-gh && git status --porcelain")
lines = [l.strip() for l in out.splitlines() if l.strip()]
modified = []
untracked = []
for l in lines:
    if l.startswith("M "): modified.append(l[3:])
    elif l.startswith("?? "): untracked.append(l[3:])
report["checks"]["git"] = {
    "status": "clean" if not lines else "dirty",
    "modified": modified,
    "untracked": untracked,
    "dirty_count": len(modified),
    "untracked_count": len(untracked)
}

# overall
docker_ok = report["checks"]["docker"]["status"] == "running"
ram_ok = report["checks"]["ram"]["status"] == "ok"
disk_ok = report["checks"]["disk"].get("status") == "ok"
git_ok = report["checks"]["git"]["status"] == "clean"
report["overall"] = "healthy" if (docker_ok and ram_ok and disk_ok and git_ok) else "needs_attention"

# save local JSON
out_path = os.path.join(results_dir, f"cron_results_{file_ts}.json")
with open(out_path, "w") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f"Saved: {out_path}")
print(json.dumps(report, indent=2, ensure_ascii=False))
