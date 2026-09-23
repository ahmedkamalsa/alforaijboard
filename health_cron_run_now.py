#!/usr/bin/env python3
"""Health check + Supabase push — single script, robust with retries."""
from __future__ import annotations
import os, sys, json, datetime, urllib.request, urllib.error, subprocess, time
from pathlib import Path

PROJECT_ID  = "bwspcsiazbwrrxpgoldx"
SUPABASE_URL = f"https://{PROJECT_ID}.supabase.co"
API_KEY_ENV = "SUPABASE_ANON_KEY"
R = Path(r"C:/Users/hello/alforaijboard-gh")
OUT_JSON = R / "cron_results" / "latest_health.json"
HIST_JSON = R / "cron_results_local.json"
TABLE = "cron_results"

def run(cmd, timeout=25):
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()
    except Exception as e:
        return -9, "", repr(e)

def kv_int(text, key):
    for line in text.splitlines():
        s = line.strip()
        if s.lower().startswith(key.lower() + "="):
            try:
                return int(s.split("=",1)[1].strip())
            except ValueError:
                return None
    return None

def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")

# ---------- 1. DOCKER ----------
rc, out, err = run("docker ps --format '{{.Names}}'")
containers = [c for c in out.splitlines() if c.strip()] if rc == 0 else []
docker_status = "RUNNING" if rc == 0 else "NOT_RUNNING"
docker_detail = (f"Docker Desktop daemon running. {len(containers)} container(s): "
                 f"{', '.join(containers) if containers else 'none'}") if rc == 0 \
                 else f"Daemon down: {err[:200] if err else 'npipe unavailable'}"
if rc != 0:
    rc2, _, err2 = run("sc start 'Docker Desktop'", timeout=20)
    if rc2 == 0:
        time.sleep(9)
        rc3, out3, err3 = run("docker ps --format '{{.Names}}'")
        if rc3 == 0 and out3.strip():
            docker_status = "RESTARTED"
            docker_detail = f"Restarted OK. Containers: {', '.join([c for c in out3.splitlines() if c.strip()])}"
        else:
            docker_detail += f" | Restart issued but ps failed: {err3[:100]}"
    else:
        docker_detail += f" | Restart failed: {err2[:100]}"

# ---------- 2. RAM ----------
rc, out, err = run("wmic OS get FreePhysicalMemory,TotalVisibleMemorySize /VALUE")
free_kb = kv_int(out, "FreePhysicalMemory")
total_kb = kv_int(out, "TotalVisibleMemorySize")
free_mb = round(free_kb/1024,1) if free_kb else None
total_mb = round(total_kb/1024,1) if total_kb else None
ram_pct = round(free_kb/total_kb*100,1) if free_kb and total_kb else None
ram_status = "OK" if free_kb and free_kb > 500*1024 else ("LOW" if free_kb else "UNKNOWN")

# ---------- 3. HERMES AGENTS ----------
rc, out, err = run("tasklist /FO CSV /NH")
hermes_pids = []
node_repls = 0
python_procs = 0
other_agent = []
if rc == 0 and out:
    for line in out.splitlines():
        parts = [p.strip().strip('"') for p in line.split(",")]
        if len(parts) < 2:
            continue
        name, pid = parts[0], parts[1]
        low = name.lower()
        if "hermes.exe" in low:
            hermes_pids.append(pid)
        if "node_repl.exe" in low:
            node_repls += 1
        if low.endswith("python.exe"):
            python_procs += 1
        if any(k in low for k in ["supabase","cron","agent","node.exe"]) and "node_repl" not in low:
            other_agent.append(name)

agent_status = "OK"
agent_parts = []
if not hermes_pids:
    agent_status = "CRITICAL"
    agent_parts.append("No hermes.exe process found")
else:
    agent_parts.append(f"{len(hermes_pids)} hermes.exe process(es): {', '.join(hermes_pids)}")
agent_parts.append(f"{len(other_agent)} related processes (node.exe/supabase/cron): {', '.join(other_agent[:8])}{'...' if len(other_agent)>8 else ''}")
agent_detail = "; ".join(agent_parts)

# ---------- 4. DISK C: ----------
rc, out, err = run("wmic logicaldisk where 'DeviceID=\"C:\"' get FreeSpace,Size /VALUE")
free_bytes = kv_int(out, "FreeSpace")
size_bytes = kv_int(out, "Size")
free_gb = round(free_bytes/1073741824,2) if free_bytes else None
size_gb = round(size_bytes/1073741824,2) if size_bytes else None
free_pct = round(free_bytes/size_bytes*100,1) if free_bytes and size_bytes else None
disk_status = "OK" if (free_pct is not None and free_pct > 10) else ("WARNING" if free_pct is not None else "UNKNOWN")

# ---------- 5. GIT ----------
git_dir = str(R)
rc, out, err = run(f"git -C \"{git_dir}\" status --porcelain")
uncommitted = [l.strip() for l in out.splitlines() if l.strip()] if rc == 0 else []
git_status = "OK" if len(uncommitted) == 0 else "WARNING"
git_detail = f"Working tree clean" if git_status=="OK" else f"{len(uncommitted)} uncommitted change(s): {uncommitted[:8]}{'...' if len(uncommitted)>8 else ''}"

# ---------- SUMMARY ----------
checks = {
    "docker": {"status": docker_status, "detail": docker_detail},
    "ram":    {"status": ram_status,  "detail": f"{free_mb} MB free / {total_mb} MB total ({ram_pct}% free)" if free_mb else "unknown"},
    "agents": {"status": agent_status,"detail": agent_detail},
    "disk":   {"status": disk_status, "detail": f"C: {free_gb} GB free ({free_pct}%) / {size_gb} GB total" if free_gb else "unknown"},
    "git":    {"status": git_status,  "detail": git_detail},
}
alerts, warnings = [], []
if docker_status != "RUNNING":
    alerts.append(f"DOCKER DOWN — {docker_detail}")
if agent_status == "CRITICAL":
    alerts.append(f"HERMES AGENTS CRITICAL — {agent_detail}")
if git_status == "WARNING":
    alerts.append(f"GIT UNCOMMITTED — {len(uncommitted)} file(s) changed on main")
if ram_status == "LOW":
    alerts.append(f"RAM LOW — {free_mb} MB free (≤ 500 MB)")
if disk_status == "WARNING":
    warnings.append(f"Disk C low — {free_pct}% free ({free_gb} GB left, threshold 10%)")
if ram_status == "OK" and ram_pct is not None and ram_pct < 20:
    warnings.append(f"RAM low-margin — {ram_pct}% free")
severity = "OK"
if alerts:
    severity = "CRITICAL" if any(a.startswith("DOCKER") or a.startswith("HERMES") for a in alerts) else "WARNING"

report = {
    "timestamp": now_iso(),
    "status": severity,
    "checks": checks,
    "alerts": alerts,
    "warnings": warnings,
    "counts": {
        "docker_containers": len(containers),
        "hermes_processes": len(hermes_pids),
        "node_repls": node_repls,
        "python_procs": python_procs,
        "git_uncommitted": len(uncommitted),
    },
}

print(json.dumps(report, ensure_ascii=False, indent=2))

# persist local
try:
    hist = []
    if HIST_JSON.exists():
        hist = json.loads(HIST_JSON.read_text(encoding="utf-8"))
    hist.append(report)
    HIST_JSON.write_text(json.dumps(hist, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaved: {OUT_JSON} | history: {HIST_JSON} ({len(hist)} entries)", file=sys.stderr)
except Exception as e:
    print(f"\n[WRITE_ERR] {e}", file=sys.stderr)

# Supabase push with retry on schema cache
def get_key():
    k = os.environ.get(API_KEY_ENV) or ""
    if k:
        return k
    dotenv = R / ".env"
    if dotenv.exists():
        for line in dotenv.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if s.startswith("SUPABASE_ANON_KEY="):
                return s.split("=",1)[1].strip().strip('"').strip("'")
    return ""

def push_with_retry(report, max_retries=3):
    key = get_key()
    if not key:
        print("\n[Supabase push SKIP] no API key", file=sys.stderr)
        report["db_status"] = "SKIPPED"
        return False
    headers = {
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
        "apikey": key,
        "Authorization": f"Bearer {key}",
    }
    body = json.dumps({"report": report}).encode("utf-8")
    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(
                f"{SUPABASE_URL}/rest/v1/{TABLE}",
                data=body, headers=headers, method="POST",
            )
            with urllib.request.urlopen(req, timeout=25) as resp:
                print(f"\n[Supabase push OK] HTTP {resp.status} (attempt {attempt})", file=sys.stderr)
                report["db_status"] = "PUSHED"
                return True
        except urllib.error.HTTPError as he:
            msg = he.read().decode("utf-8", "replace")
            code = he.code
            print(f"\n[Supabase push HTTP {code}] (attempt {attempt}) :: {msg[:250]}", file=sys.stderr)
            if code == 400 and "PGRST204" in msg and attempt < max_retries:
                print(f"  -> schema cache miss, waiting 5s before retry...", file=sys.stderr)
                time.sleep(5)
                continue
            report["db_status"] = "PUSH_FAILED"
            return False
        except Exception as e:
            print(f"\n[Supabase push ERR] (attempt {attempt}): {e}", file=sys.stderr)
            if attempt < max_retries:
                time.sleep(3)
                continue
            report["db_status"] = "PUSH_FAILED"
            return False
    report["db_status"] = "PUSH_FAILED"
    return False

push_with_retry(report)
# update local history with db_status
try:
    hist = []
    if HIST_JSON.exists():
        hist = json.loads(HIST_JSON.read_text(encoding="utf-8"))
    if hist:
        hist[-1]["db_status"] = report.get("db_status", "UNKNOWN")
        HIST_JSON.write_text(json.dumps(hist, ensure_ascii=False, indent=2), encoding="utf-8")
except Exception:
    pass
