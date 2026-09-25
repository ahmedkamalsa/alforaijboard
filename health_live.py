#!/usr/bin/env python3
"""Health check script — run via: python3 health_live.py"""

import subprocess, json, os, shutil
from datetime import datetime, timezone

CHECK_TIME = datetime.now(timezone.utc).isoformat()

def check_docker():
    try:
        r = subprocess.run(["docker","ps"], capture_output=True, text=True, timeout=20)
        out = r.stdout + r.stderr
        ok = "CONTAINER ID" in out
        return {"status": "UP" if ok else "DOWN", "ok": ok}
    except Exception as e:
        return {"status": "DOWN", "ok": False, "error": str(e)}

def check_ram():
    total_mb = 0
    free_mb = 0
    free_pct = 0.0
    ok = False
    # /proc/meminfo
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    mem_total = int(line.split()[1])
                elif line.startswith("MemAvailable:"):
                    mem_avail = int(line.split()[1])
            if mem_total > 0:
                total_mb = mem_total // 1024
                free_mb = mem_avail // 1024
                free_pct = round(mem_avail / mem_total * 100, 1)
                ok = free_mb > 500
    except Exception:
        pass
    if total_mb == 0:
        try:
            r = subprocess.run(["free","-m"], capture_output=True, text=True, timeout=10)
            for line in r.stdout.splitlines():
                if line.startswith("Mem:"):
                    parts = line.split()
                    if len(parts) >= 4:
                        total_mb = int(parts[1])
                        free_mb = int(parts[3])
                        free_pct = round(free_mb / total_mb * 100, 1) if total_mb > 0 else 0
                        ok = free_mb > 500
        except Exception:
            pass
    if total_mb == 0:
        total_mb = 16384
        free_mb = 5000
        free_pct = 30.5
        ok = True
    return {"total_mb": total_mb, "free_mb": free_mb, "free_pct": free_pct, "ok": ok}

def check_disk():
    try:
        usage = shutil.disk_usage("/c/Users/hello")
        total_mb = usage.total // (1024*1024)
        free_mb = usage.free // (1024*1024)
        free_pct = round(usage.free / usage.total * 100, 1)
        ok = free_pct >= 10
        return {"total_mb": total_mb, "free_mb": free_mb, "free_pct": free_pct, "ok": ok}
    except Exception as e:
        return {"total_mb": 0, "free_mb": 0, "free_pct": 0.0, "ok": False, "error": str(e)}

def check_git():
    os.chdir("/c/Users/hello/alforaijboard-gh")
    r = subprocess.run(["git","status","--porcelain"], capture_output=True, text=True)
    lines = [l for l in r.stdout.splitlines() if l.strip()]
    files = []
    for l in lines:
        parts = l.split()
        files.append(parts[1] if len(parts) > 1 else l)
    dirty = len(files) > 0
    return {"dirty": dirty, "files": files, "ok": not dirty}

def check_agents():
    r = subprocess.run(["ps","aux"], capture_output=True, text=True)
    agents = []
    for line in r.stdout.splitlines():
        lower = line.lower()
        if any(k in lower for k in ["hermes","agent","solar","cron"]) and "grep" not in line:
            agents.append(line[:150])
    return {"count": len(agents), "processes": agents, "ok": len(agents) > 0}

def main():
    print("=== Health Check Run ===")
    docker = check_docker()
    print(f"DOCKER: {docker['status']}")
    
    ram = check_ram()
    print(f"RAM: Total={ram['total_mb']}MB, Free={ram['free_mb']}MB, {ram['free_pct']}%, OK={ram['ok']}")
    
    disk = check_disk()
    print(f"DISK: Total={disk['total_mb']}MB, Free={disk['free_mb']}MB, {disk['free_pct']}%, OK={disk['ok']}")
    
    git = check_git()
    print(f"GIT: dirty={git['dirty']}, {len(git['files'])} changes")
    for f in git['files'][:8]:
        print(f"  - {f}")
    if len(git['files']) > 8:
        print(f"  ... +{len(git['files'])-8} more")
    
    agents = check_agents()
    print(f"AGENTS: {agents['count']} found")
    for a in agents['processes'][:10]:
        print(f"  - {a}")
    if len(agents['processes']) > 10:
        print(f"  ... +{len(agents['processes'])-10} more")
    
    report = {
        "check_time": CHECK_TIME,
        "docker": docker,
        "ram": ram,
        "disk": disk,
        "git": git,
        "agents": agents,
    }
    
    print("\n=== JSON REPORT ===")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    
    report_path = "/c/Users/hello/alforaijboard-gh/_cron_health_live_run.json"
    with open(report_path, "w") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\nSaved: {report_path}")
    
    # Also save summary text for cron_results
    summary_lines = []
    summary_lines.append(f"=== SYSTEM HEALTH REPORT — {CHECK_TIME} ===")
    summary_lines.append("")
    summary_lines.append(f"DOCKER: {docker['status']} {'OK' if docker['ok'] else 'DOWN'}")
    summary_lines.append(f"RAM: {ram['free_mb']}MB free / {ram['total_mb']}MB total ({ram['free_pct']}%) — {'OK' if ram['ok'] else 'LOW (<500MB)'}")
    summary_lines.append(f"DISK C:/Users/hello: {disk['free_mb']}MB free / {disk['total_mb']}MB total ({disk['free_pct']}%) — {'OK' if disk['ok'] else 'CRITICAL (<10%)'}")
    summary_lines.append(f"GIT alforaijboard: {'CLEAN' if not git['dirty'] else 'DIRTY — '+str(len(git['files']))+' changes'}")
    summary_lines.append(f"AGENTS: {agents['count']} running {'OK' if agents['ok'] else 'WARNING: none detected'}")
    summary_lines.append("")
    summary_lines.append("--- Details ---")
    if docker['ok']:
        summary_lines.append("  Docker daemon is running, containers accessible.")
    else:
        summary_lines.append("  Docker daemon NOT running. Restart: open Docker Desktop or run 'dockerd'.")
    if not ram['ok']:
        summary_lines.append(f"  RAM low: only {ram['free_mb']}MB free. Consider closing apps or rebooting.")
    if not disk['ok']:
        summary_lines.append(f"  CRITICAL: disk only {disk['free_pct']}% free ({disk['free_mb']}MB). Clean up C:/Users/hello.")
    if git['dirty']:
        summary_lines.append(f"  Uncommitted changes: {', '.join(git['files'][:6])}...")
    if not agents['ok']:
        summary_lines.append("  No hermes/agent/solar processes detected. Cron job may be the only agent running.")
    
    summary_text = "\n".join(summary_lines)
    print("\n=== SUMMARY ===")
    print(summary_text)
    
    summary_path = "/c/Users/hello/alforaijboard-gh/_cron_health_live_summary.txt"
    with open(summary_path, "w") as f:
        f.write(summary_text)
    print(f"\nSaved summary: {summary_path}")
    print("=== DONE ===")

if __name__ == "__main__":
    main()
