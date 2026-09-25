import os, json, subprocess, datetime, re

def run(cmd, timeout=15):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip(), r.stderr.strip(), r.returncode
    except Exception as e:
        return "", str(e), -1

ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M")
lines = []
alerts = []
warnings = []

# 1. Docker
out, err, rc = run(["docker", "ps", "--format", "{{.Names}}"])
if rc == 0 and out:
    containers = [c for c in out.split("\n") if c.strip()]
    lines.append(f"[DOCKER] OK — {len(containers)} container(s)" + (f": {', '.join(containers)}" if containers else ""))
    if not containers:
        warnings.append("No containers running (daemon OK)")
else:
    lines.append(f"[DOCKER] DOWN — {err or 'daemon not reachable'}")
    alerts.append(f"Docker daemon DOWN: {err or 'unknown'}")

# 2. RAM via wmic (KB)
out, err, rc = run(["wmic", "os", "get", "FreePhysicalMemory,TotalVisibleMemorySize", "/VALUE"])
if rc == 0 and "FreePhysicalMemory=" in out:
    free_kb = int([l for l in out.split("\n") if l.startswith("FreePhysicalMemory=")][0].split("=")[1])
    total_kb = int([l for l in out.split("\n") if l.startswith("TotalVisibleMemorySize=")][0].split("=")[1])
    free_mb = round(free_kb / 1024)
    total_gb = round(total_kb / (1024*1024), 2)
    pct = round(free_kb / total_kb * 100, 1)
    lines.append(f"[RAM] {'OK' if free_mb > 500 else 'LOW'} — {free_mb} MB free ({pct}%) / {total_gb} GB total")
    if free_mb <= 500:
        alerts.append(f"RAM free ({free_mb} MB) <= 500 MB threshold")
else:
    lines.append(f"[RAM] ERROR — {err}")
    alerts.append("RAM check failed")

# 3. Hermes agents via tasklist
procs = []
for img in ["hermes.exe", "node.exe", "python.exe"]:
    out, err, rc = run(["tasklist", "/FI", f"IMAGENAME eq {img}", "/FO", "CSV", "/NH"])
    if rc == 0 and out:
        for line in out.split("\n"):
            line = line.strip()
            if not line:
                continue
            parts = re.split(r',(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)', line)
            parts = [p.strip().strip('"') for p in parts]
            if len(parts) >= 5:
                pid = parts[1]
                mem_str = parts[4].replace(",", "").replace(" K", "")
                try:
                    mem_kb = int(mem_str)
                except:
                    mem_kb = 0
                procs.append(f"PID={pid} {img} RAM={round(mem_kb/1024,1)}MB")
if procs:
    lines.append(f"[AGENTS] OK — {len(procs)} process(es) found")
    for p in procs[:15]:
        lines.append(f"  {p}")
else:
    lines.append("[AGENTS] None detected — verify Hermes is running")
    alerts.append("No Hermes agent processes found")

# 4. Disk C: via wmic
out, err, rc = run(["wmic", "logicaldisk", "where", "DeviceID='C:'", "get", "Size,FreeSpace", "/VALUE"])
if rc == 0 and "FreeSpace=" in out:
    free_bytes = int([l for l in out.split("\n") if l.startswith("FreeSpace=")][0].split("=")[1])
    size_bytes = int([l for l in out.split("\n") if l.startswith("Size=")][0].split("=")[1])
    free_gb = round(free_bytes / (1024**3), 2)
    size_gb = round(size_bytes / (1024**3), 2)
    free_pct = round(free_bytes / size_bytes * 100, 1)
    lines.append(f"[DISK C:] {'OK' if free_pct > 10 else ('LOW' if free_pct > 5 else 'CRITICAL')} — {free_gb} GB free ({free_pct}%) / {size_gb} GB total")
    if free_pct <= 10:
        alerts.append(f"Disk C: free space ({free_pct}%) <= 10% threshold")
else:
    lines.append(f"[DISK] ERROR — {err}")
    alerts.append("Disk check failed")

# 5. Git
out, err, rc = run(["git", "-C", "C:/Users/hello/alforaijboard-gh", "status", "--porcelain"])
if rc == 0:
    dirty = [l for l in out.split("\n") if l.strip()]
    if dirty:
        lines.append(f"[GIT] DIRTY — {len(dirty)} uncommitted change(s):")
        for d in dirty[:10]:
            lines.append(f"  {d}")
        if len(dirty) > 10:
            lines.append(f"  ... and {len(dirty)-10} more")
        alerts.append(f"Git repo has {len(dirty)} uncommitted change(s)")
    else:
        lines.append("[GIT] CLEAN — no uncommitted changes")
else:
    lines.append(f"[GIT] ERROR — {err}")
    alerts.append("Git check failed")

lines.append("")
if alerts:
    lines.append(f"!!! {len(alerts) + len(warnings)} ISSUE(S): {len(alerts)} alert(s), {len(warnings)} warning(s)")
    for a in alerts:
        lines.append(f"  ! {a}")
    for w in warnings:
        lines.append(f"  ~ {w}")
else:
    lines.append(f"All systems nominal. {len(warnings)} minor warning(s).")

report_text = "\n".join(lines)
status = "error" if alerts else "success"

print(report_text)
print(f"\n[SAVED] timestamp={ts} status={status}")

path = "C:/Users/hello/alforaijboard-gh/_cron_health_latest.json"
with open(path, "w") as f:
    json.dump({"timestamp": ts, "report": report_text, "status": status, "alerts": len(alerts)}, f, indent=2)
print(f"[LOCAL] {path}")
