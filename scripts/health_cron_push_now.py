#!/usr/bin/env python3
"""
alforaijboard-gh hourly health check → Supabase cron_results push + local mirror.
Tuned for Windows (MSYS2 bash) + cron (no user present).
Uses wmic for RAM/Disk/CPU (free/vmstat unavailable).
"""
import json, subprocess, sys, datetime, urllib.request, urllib.error, os

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://bwspcsiazbwrrxpgoldx.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY", "sb_publishable_c84oHQS94osRqw_SiTIqMg_8icxvatZ")
TABLE = "cron_results"
SHEET = SUPABASE_URL.rstrip("/") + "/rest/v1/" + TABLE
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal",
}

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=40)
    return r.stdout.strip(), r.stderr.strip(), r.returncode

def now_iso():
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")

def mem_status():
    out, err, rc = run("wmic OS get FreePhysicalMemory,TotalVisibleMemorySize /format:list")
    free = total = None
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("FreePhysicalMemory="):
            free = int(line.split("=",1)[1]) // 1024
        elif line.startswith("TotalVisibleMemorySize="):
            total = int(line.split("=",1)[1]) // 1024
    if free is None or total is None:
        return "UNKNOWN", f"wmic mem failed: {err or out[:200]}"
    pct = round(100.0 * (total - free) / total, 1)
    return ("OK" if free >= 500 else "WARNING"), f"{free} MB free / {total} MB total ({pct}% used)"

def disk_status():
    out, err, rc = run("wmic logicaldisk where \"DeviceID='C:'\" get FreeSpace,Size /format:list")
    free = total = None
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("FreeSpace="):
            free = int(line.split("=",1)[1])
        elif line.startswith("Size="):
            total = int(line.split("=",1)[1])
    if free is None or total is None:
        return "UNKNOWN", f"wmic disk failed: {err or out[:200]}"
    gb_free = round(free / 1e9, 2)
    gb_total = round(total / 1e9, 2)
    pct_free = round(100.0 * free / total, 1)
    status = "CRITICAL" if pct_free < 10 else "OK"
    return status, f"C: {gb_free} GB free ({pct_free}%) / {gb_total} GB total"

def docker_status():
    out, err, rc = run("docker ps -q 2>&1")
    if rc != 0 or "cannot find the file specified" in out or "failed to connect" in out:
        return "DOWN", f"docker daemon unreachable: {out[:200]}"
    containers = [c for c in out.splitlines() if c.strip()]
    if not containers:
        return "IDLE", "no running containers"
    return "UP", f"{len(containers)} container(s) running"

def git_status(repo="/c/Users/hello/alforaijboard-gh"):
    out, err, rc = run(f"cd {repo} && git status --short 2>&1")
    lines = [l for l in out.splitlines() if l.strip()]
    modified = [l for l in lines if l[0] in "MARC"]
    untracked = [l for l in lines if l.startswith("??")]
    return modified, untracked, len(lines)

def agents():
    out, err, rc = run("wmic process where \"name='node.exe'\" get ProcessId,WorkingSetSize /format:list 2>&1")
    pids = []
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("ProcessId="):
            try:
                pids.append(int(line.split("=",1)[1]))
            except ValueError:
                pass
    return len(pids), out

def push(payload):
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(SHEET, data=body, headers=HEADERS, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, resp.read().decode("utf-8","replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8","replace")
    except Exception as e:
        return None, str(e)

def main():
    ts = now_iso()
    ram_st, ram_detail = mem_status()
    disk_st, disk_detail = disk_status()
    docker_st, docker_detail = docker_status()
    mod, unk, total_git = git_status()
    node_count, _ = agents()

    alerts = []
    warnings = []
    if docker_st != "UP":
        alerts.append(f"DOCKER DOWN — {docker_detail}")
    if ram_st == "WARNING":
        warnings.append(f"RAM LOW — {ram_detail}")
    if disk_st == "CRITICAL":
        alerts.append(f"DISK CRITICAL — {disk_detail}")
    if mod or unk:
        warnings.append(f"GIT UNC — {total_git} file(s): {len(mod)} mod, {len(unk)} untracked")
    if node_count < 3:
        alerts.append(f"AGENTS LOW — only {node_count} node.exe processes seen")

    if alerts:
        status = "CRITICAL"
    elif warnings:
        status = "WARNING"
    else:
        status = "OK"

    # Match the onclick_updatable schema: id, name, status, message, duration_ms, records_affected, created_at
    payload = {
        "name": f"health_cron_{ts[:10].replace('-','')}",
        "status": "success" if status == "OK" else ("error" if status == "CRITICAL" else "warning"),
        "message": "; ".join(alerts) if alerts else ("; ".join(warnings) if warnings else "OK"),
        "duration_ms": 0,
        "records_affected": 1,
        "created_at": ts,
    }

    print("=== HEALTH REPORT", ts, "===")
    print("status:", status)
    print("docker:", docker_st, "-", docker_detail[:120])
    print("ram:", ram_st, "-", ram_detail)
    print("disk:", disk_st, "-", disk_detail)
    print("git:", "DIRTY" if (mod or unk) else "CLEAN", "-", total_git, "uncommitted")
    print("agents:", node_count, "node.exe")
    print("alerts:", len(alerts), "warnings:", len(warnings))
    print("payload:", json.dumps(payload))

    http_st, http_body = push(payload)
    if http_st in (200, 201):
        print(f"[OK] Pushed to {SUPABASE_URL}/{TABLE} → {http_st}")
    else:
        print(f"[FAIL] Supabase push → HTTP {http_st}: {http_body[:200]}")
    local = "/c/Users/hello/alforaijboard-gh/cron_results/latest_health.json"
    os.makedirs(os.path.dirname(local), exist_ok=True)
    with open(local, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"[OK] Local mirror → {local}")
    return 0 if http_st in (200,201) else 1

if __name__ == "__main__":
    sys.exit(main())
