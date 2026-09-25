#!/usr/bin/env python3
"""System health check - runs directly via terminal, no -c flag needed."""
import json, os, subprocess, shutil
from datetime import datetime, timezone

REPORT = {}
ALERTS = []
WARNINGS = []

def run(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except Exception as e:
        return -1, "", str(e)

# 1. Docker
rc, out, err = run(["docker", "ps", "--format", "{{.Names}}"])
if rc == 0:
    names = [n for n in out.split("\n") if n.strip()]
    REPORT["docker"] = {"status": "OK", "containers": names, "count": len(names)}
    if not names:
        WARNINGS.append("Docker daemon OK but no containers running")
else:
    REPORT["docker"] = {"status": "DOWN", "error": err[:200]}
    ALERTS.append(f"DOCKER DOWN: {err[:150]}")

# 2. RAM — use psutil if available, else df-style
try:
    import psutil
    mem = psutil.virtual_memory()
    free_mb = mem.available / (1024*1024)
    total_gb = mem.total / (1024*1024*1024)
    REPORT["ram"] = {"free_mb": round(free_mb,1), "total_gb": round(total_gb,2), "pct": round(mem.available/mem.total*100,1)}
    if free_mb <= 500:
        ALERTS.append(f"RAM low: {free_mb:.0f} MB free (threshold 500 MB)")
    else:
        REPORT["ram"]["status"] = "OK"
except ImportError:
    rc2, out2, err2 = run(["free", "-m"])
    REPORT["ram"] = {"raw": out2[:300]}
    if "available" in out2.lower() or "free" in out2.lower():
        lines = out2.split("\n")
        for l in lines:
            if l.startswith("Mem:"):
                parts = l.split()
                if len(parts) >= 4:
                    free_mb = int(parts[3])
                    total_mb = int(parts[1])
                    REPORT["ram"]["free_mb"] = free_mb
                    REPORT["ram"]["total_mb"] = total_mb
                    if free_mb <= 500:
                        ALERTS.append(f"RAM low: {free_mb} MB free")

# 3. Hermes agents / processes
rc3, out3, err3 = run(["ps", "aux"])
procs = []
if rc3 == 0:
    for line in out3.split("\n"):
        low = line.lower()
        if any(x in low for x in ["hermes", "python", "node", "git"]):
            procs.append(line.strip())
REPORT["processes"] = {"count": len(procs), "sample": procs[:10]}
if len(procs) == 0:
    WARNINGS.append("No Hermes/python/node processes detected (expected for single-run cron)")
else:
    REPORT["processes"]["status"] = "OK"

# 4. Disk C:
try:
    usage = shutil.disk_usage("C:/")
    free_gb = usage.free / (1024**3)
    total_gb = usage.total / (1024**3)
    free_pct = (usage.free / usage.total) * 100
    REPORT["disk_c"] = {"free_gb": round(free_gb,2), "total_gb": round(total_gb,2), "free_pct": round(free_pct,1)}
    if free_pct <= 10:
        ALERTS.append(f"Disk C: {free_pct:.1f}% free — critical (< 10%)")
    elif free_pct <= 5:
        WARNINGS.append(f"Disk C: {free_pct:.1f}% free — low (< 5%)")
    else:
        REPORT["disk_c"]["status"] = "OK"
except Exception as e:
    REPORT["disk_c"] = {"error": str(e)[:200]}
    ALERTS.append(f"Disk check failed: {e}")

# 5. Git
os.chdir("C:/Users/hello/alforaijboard-gh")
rc5, out5, err5 = run(["git", "status", "--porcelain"])
if rc5 == 0:
    dirty = [l for l in out5.split("\n") if l.strip()]
    REPORT["git"] = {"status": "DIRTY" if dirty else "CLEAN", "count": len(dirty), "changes": dirty[:10]}
    if dirty:
        ALERTS.append(f"Git has {len(dirty)} uncommitted change(s)")
else:
    REPORT["git"] = {"status": "ERROR", "error": err5[:100]}
    ALERTS.append(f"Git check failed: {err5[:100]}")

# Summary
REPORT["timestamp"] = datetime.now(timezone.utc).isoformat()
REPORT["alerts"] = ALERTS
REPORT["warnings"] = WARNINGS
REPORT["all_ok"] = len(ALERTS) == 0

print(json.dumps(REPORT, indent=2, ensure_ascii=False))

# Save locally
with open("C:/Users/hello/alforaijboard-gh/_cron_health_latest.json", "w", encoding="utf-8") as f:
    json.dump(REPORT, f, indent=2, ensure_ascii=False)
print("\nLocal report saved.")
