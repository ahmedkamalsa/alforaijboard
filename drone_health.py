#!/usr/bin/env python3
"""CI-friendly health check (no Supabase). Linux/Mac/Windows. Writes report + JSON."""
from __future__ import annotations
import os, sys, json, subprocess, datetime, platform
from pathlib import Path

R = Path(os.environ.get("REPO_DIR", "/c/Users/hello/alforaijboard-gh"))
OUT_JSON = R / "cron_results" / "latest_health.json"
HIST_JSON = R / "cron_results_local.json"

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

def humantime(dt):
    return dt.strftime("%Y-%m-%d %H:%M %Z")

# ---- DOCKER ----
rc, out, err = run("docker ps --format '{{.Names}}'" if platform.system()!="Windows" else "docker ps --format '{{.Names}}'")
containers = [c for c in out.splitlines() if c.strip()] if rc == 0 else []
docker_status = "RUNNING" if rc == 0 else "DOWN"
docker_detail = (f"Docker daemon running. {len(containers)} container(s): "
                 f"{', '.join(containers) if containers else 'none'}") if rc == 0 \
                 else f"Docker daemon unreachable: {err[:120] if err else 'no docker'}. Restart Docker Desktop manually on Windows host."

# ---- RAM ----
if platform.system() == "Windows":
    rc, out, err = run("wmic OS get FreePhysicalMemory,TotalVisibleMemorySize /VALUE")
    free_kb = kv_int(out, "FreePhysicalMemory")
    total_kb = kv_int(out, "TotalVisibleMemorySize")
else:
    rc, out, err = run("free -m")
    free_kb = None; total_kb = None
    if rc == 0 and out:
        for line in out.splitlines():
            if line.startswith("Mem:"):
                parts = line.split()
                try:
                    total_kb = int(parts[1]) * 1024
                    free_kb = int(parts[3]) * 1024
                except Exception:
                    pass
free_mb = round(free_kb/1024,1) if free_kb else None
total_mb = round(total_kb/1024,1) if total_kb else None
ram_pct = round(free_kb/total_kb*100,1) if free_kb and total_kb else None
ram_status = "OK" if free_kb and free_kb > 500*1024 else ("LOW" if free_kb else "UNKNOWN")
ram_detail = f"{free_mb} MB free / {total_mb} MB total ({ram_pct}% free)" if free_mb else "unknown"

# ---- HERMES AGENTS ----
rc, out, err = run("tasklist /FO CSV /NH" if platform.system()=="Windows" else "ps -eo comm,pid --no-headers")
hermes_pids = []
node_repls = 0
python_procs = 0
related = []
if platform.system() == "Windows" and rc == 0 and out:
    for line in out.splitlines():
        parts = [p.strip().strip('"') for p in line.split(",")]
        if len(parts) < 2: continue
        name, pid = parts[0], parts[1]
        low = name.lower()
        if "hermes.exe" in low: hermes_pids.append(pid)
        if "node_repl.exe" in low: node_repls += 1
        if low.endswith("python.exe"): python_procs += 1
        if any(k in low for k in ["supabase","cron","agent","node.exe"]) and "node_repl" not in low:
            related.append(name)
else:
    if rc == 0 and out:
        for line in out.splitlines():
            parts = line.strip().split()
            if len(parts) < 2: continue
            pid, comm = parts[-1], " ".join(parts[:-1])
            low = comm.lower()
            if "hermes" in low: hermes_pids.append(pid)
            if "node" in low: node_repls += 1
            if "python" in low: python_procs += 1

agent_status = "OK"
agent_parts = []
if not hermes_pids:
    agent_status = "CRITICAL"
    agent_parts.append("No hermes process found")
else:
    agent_parts.append(f"{len(hermes_pids)} hermes process(es)")
agent_parts.append(f"{len(related)} related processes")
agent_detail = "; ".join(agent_parts)

# ---- DISK ----
if platform.system() == "Windows":
    rc, out, err = run("wmic logicaldisk where 'DeviceID=\"C:\"' get FreeSpace,Size /VALUE")
    free_bytes = kv_int(out, "FreeSpace")
    size_bytes = kv_int(out, "Size")
else:
    rc, out, err = run("df -B1 /")
    free_bytes = size_bytes = None
    if rc == 0 and out:
        lines = out.splitlines()
        if len(lines) >= 2:
            parts = lines[1].split()
            if len(parts) >= 4:
                try:
                    size_bytes = int(parts[1])
                    free_bytes = int(parts[3])
                except Exception:
                    pass
free_gb = round(free_bytes/1073741824,2) if free_bytes else None
size_gb = round(size_bytes/1073741824,2) if size_bytes else None
free_pct = round(free_bytes/size_bytes*100,1) if free_bytes and size_bytes else None
disk_status = "OK" if (free_pct is not None and free_pct > 10) else ("WARNING" if free_pct is not None else "UNKNOWN")
disk_detail = f"Root: {free_gb} GB free ({free_pct}%) / {size_gb} GB total" if free_gb else "unknown"

# ---- GIT ----
git_dir = str(R)
rc, out, err = run(f"git -C \"{git_dir}\" status --porcelain")
uncommitted = [l.strip() for l in out.splitlines() if l.strip()] if rc == 0 else []
git_status = "OK" if len(uncommitted) == 0 else "WARNING"
git_detail = f"Clean" if git_status=="OK" else f"{len(uncommitted)} change(s)"

checks = {
    "docker": {"status": docker_status, "detail": docker_detail},
    "ram":    {"status": ram_status,  "detail": ram_detail},
    "agents": {"status": agent_status,"detail": agent_detail},
    "disk":   {"status": disk_status, "detail": disk_detail},
    "git":    {"status": git_status,  "detail": git_detail},
}
alerts, warnings = [], []
if docker_status == "DOWN": alerts.append("DOCKER DOWN — restart Docker Desktop manually on Windows host")
if agent_status == "CRITICAL": alerts.append("HERMES AGENTS CRITICAL — hermes process not found")
if git_status == "WARNING": alerts.append(f"GIT UNCOMMITTED — {len(uncommitted)} file(s) changed")
if ram_status == "LOW": alerts.append(f"RAM LOW — {free_mb} MB free")
if disk_status == "WARNING": warnings.append(f"Disk low — {free_pct}% free ({free_gb} GB left)")
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
    "db_status": "SKIPPED_CI_LOCAL_ONLY",
}
print(json.dumps(report, ensure_ascii=False, indent=2))

try:
    hist = []
    if HIST_JSON.exists():
        hist = json.loads(HIST_JSON.read_text(encoding="utf-8"))
    hist.append(report)
    HIST_JSON.write_text(json.dumps(hist, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaved: {OUT_JSON} | history: {HIST_JSON}", file=sys.stderr)
except Exception as e:
    print(f"\n[WRITE_ERR] {e}", file=sys.stderr)
