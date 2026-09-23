#!/usr/bin/env python3
"""Health check — writes JSON report to stdout and pushes to Supabase if key available."""

import os
import json
import subprocess
import datetime
import urllib.request
import urllib.error

def run(cmd, timeout=15):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=False)
        return r.stdout.strip(), r.stderr.strip(), r.returncode
    except Exception as e:
        return "", str(e), -1

def main():
    ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M")
    lines = []
    alerts = []
    warnings = []

    # 1. Docker
    out, err, rc = run(["docker", "ps", "--format", "{{.Names}}"])
    if rc == 0 and out:
        containers = [c for c in out.split("\n") if c.strip()]
        status = f"OK — {len(containers)} container(s): {', '.join(containers)}" if containers else "OK — daemon running, no containers"
        lines.append(f"[DOCKER] {status}")
        if not containers:
            warnings.append("No containers running (daemon OK)")
    else:
        status = f"DOWN — {err or 'daemon not reachable'}"
        lines.append(f"[DOCKER] {status}")
        alerts.append(f"Docker daemon DOWN: {err or 'unknown'}")
        # attempt restart via taskkill/start logic — skip here, report only

    # 2. RAM
    out, err, rc = run(["wmic", "os", "get", "FreePhysicalMemory,TotalVisibleMemorySize", "/VALUE"])
    if rc == 0 and "FreePhysicalMemory=" in out:
        free_kb = int([l for l in out.split("\n") if l.startswith("FreePhysicalMemory=")][0].split("=")[1])
        total_kb = int([l for l in out.split("\n") if l.startswith("TotalVisibleMemorySize=")][0].split("=")[1])
        free_mb = round(free_kb / 1024, 1)
        total_gb = round(total_kb / (1024*1024), 2)
        pct = round(free_kb / total_kb * 100, 1)
        ram_status = "OK" if free_mb > 500 else "LOW"
        lines.append(f"[RAM] {ram_status} — {free_mb} MB free ({pct}%) / {total_gb} GB total")
        if free_mb <= 500:
            alerts.append(f"RAM free ({free_mb} MB) <= 500 MB threshold")
    else:
        lines.append(f"[RAM] ERROR — {err}")
        alerts.append("RAM check failed")

    # 3. Hermes agents
    procs = []
    for img in ["hermes.exe", "node.exe", "python.exe"]:
        out, err, rc = run(["tasklist", "/FI", f"IMAGENAME eq {img}", "/FO", "CSV"])
        if rc == 0 and out:
            for line in out.split("\n")[1:]:
                parts = line.split(",")
                if len(parts) >= 2:
                    pid = parts[1].strip()
                    mem_str = parts[4].strip().replace(",", "") if len(parts) > 4 else "0"
                    try:
                        mem_kb = int(mem_str)
                    except:
                        mem_kb = 0
                    procs.append({"pid": pid, "name": img, "mem_mb": round(mem_kb/1024, 1)})
    if procs:
        lines.append(f"[AGENTS] OK — {len(procs)} process(es) found")
        for p in procs[:10]:
            lines.append(f"  PID={p['pid']} {p['name']} RAM={p['mem_mb']}MB")
    else:
        lines.append("[AGENTS] None detected — verify Hermes is running")
        alerts.append("No Hermes agent processes found")

    # 4. Disk C:
    out, err, rc = run(["wmic", "logicaldisk", "where", "DeviceID='C:'", "get", "Size,FreeSpace", "/VALUE"])
    if rc == 0 and "FreeSpace=" in out:
        free_bytes = int([l for l in out.split("\n") if l.startswith("FreeSpace=")][0].split("=")[1])
        size_bytes = int([l for l in out.split("\n") if l.startswith("Size=")][0].split("=")[1])
        free_gb = round(free_bytes / (1024**3), 2)
        size_gb = round(size_bytes / (1024**3), 2)
        free_pct = round(free_bytes / size_bytes * 100, 1)
        disk_status = "OK" if free_pct > 10 else ("LOW" if free_pct > 5 else "CRITICAL")
        lines.append(f"[DISK C:] {disk_status} — {free_gb} GB free ({free_pct}%) / {size_gb} GB total")
        if free_pct <= 10:
            alerts.append(f"Disk C: free space ({free_pct}%) <= 10% threshold")
    else:
        lines.append(f"[DISK] ERROR — {err}")
        alerts.append("Disk check failed")

    # 5. Git
    git_dir = "C:/Users/hello/alforaijboard-gh"
    out, err, rc = run(["git", "-C", git_dir, "status", "--porcelain"])
    if rc == 0:
        dirty = [l for l in out.split("\n") if l.strip()]
        if dirty:
            lines.append(f"[GIT] DIRTY — {len(dirty)} uncommitted change(s):")
            for d in dirty:
                lines.append(f"  {d}")
            alerts.append(f"Git repo has {len(dirty)} uncommitted change(s)")
        else:
            lines.append("[GIT] CLEAN — no uncommitted changes")
    else:
        lines.append(f"[GIT] ERROR — {err}")
        alerts.append("Git check failed")

    # Summary
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

    # Push to Supabase
    anon_key = os.environ.get("SUPABASE_ANON_KEY", "")
    if anon_key and len(anon_key) > 10:
        url = "https://bwspcsiazbwrrxpgoldx.supabase.co/rest/v1/cron_results"
        payload = json.dumps({
            "name": f"health_check_{ts}",
            "status": status,
            "message": report_text,
            "duration_ms": None,
            "records_affected": None,
            "created_at": ts
        }).encode()
        req = urllib.request.Request(url, data=payload, headers={
            "Content-Type": "application/json",
            "apikey": anon_key,
            "Authorization": f"Bearer {anon_key}"
        })
        try:
            resp = urllib.request.urlopen(req, timeout=10)
            lines.append(f"\n[DB] Pushed to Supabase cron_results (HTTP {resp.status})")
        except Exception as e:
            lines.append(f"\n[DB] Supabase push failed (non-fatal): {e}")
    else:
        lines.append("\n[DB] SUPABASE_ANON_KEY not set — skipping push")

    print(report_text)
    # Also write to file
    path = f"C:/Users/hello/alforaijboard-gh/_cron_health_latest.json"
    with open(path, "w") as f:
        json.dump({"timestamp": ts, "report": report_text, "status": status, "alerts": len(alerts)}, f, indent=2)
    print(f"\n[SAVED] {path}")

if __name__ == "__main__":
    main()
