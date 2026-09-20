#!/usr/bin/env python3
"""System health check — run via cron, produces report + pushes to Supabase."""
import os, json, datetime, subprocess, sys, requests

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
        return r.returncode, (r.stdout or ""), (r.stderr or "")
    except Exception as e:
        return -1, "", str(e)

report = {"timestamp": timestamp, "file_ts": file_ts, "checks": {}}
alerts = []
warnings_list = []

# 1) Docker
rc, out, err = run_cmd("docker ps --format '{{.Names}}'")
docker_status = "running" if rc == 0 else "not_running"
docker_containers = []
if rc == 0:
    docker_containers = [l.strip() for l in out.splitlines() if l.strip()]
report["checks"]["docker"] = {
    "status": docker_status,
    "container_count": len(docker_containers),
    "containers": docker_containers[:10],
    "severity": "info" if docker_status == "running" else "error"
}
if docker_status != "running":
    alerts.append(f"Docker daemon not running — manual restart required (docker ps failed)")
elif len(docker_containers) == 0:
    warnings_list.append("Docker daemon OK but no containers running")

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
if ram_status == "low":
    alerts.append(f"RAM free ({round(free_mb)} MB) <= 500 MB threshold")

# 3) Processes
rc, out, err = run_cmd("wmic cpu get loadpercentage")
load = 0
for line in out.splitlines():
    s = line.strip()
    if s.isdigit():
        load = int(s)

# Count node/python/hermes processes
rc_tl, out_tl, _ = run_cmd("tasklist /FI \"IMAGENAME eq node.exe\" /FO CSV 2>&1")
node_count = sum(1 for l in out_tl.splitlines() if l.strip() and 'node.exe' in l.lower()) - 1 if rc_tl == 0 else 0
rc_tl2, out_tl2, _ = run_cmd("tasklist /FI \"IMAGENAME eq python.exe\" /FO CSV 2>&1")
python_count = sum(1 for l in out_tl2.splitlines() if l.strip() and 'python.exe' in l.lower()) - 1 if rc_tl2 == 0 else 0
rc_tl3, out_tl3, _ = run_cmd("tasklist /FI \"IMAGENAME eq hermes.exe\" /FO CSV 2>&1")
hermes_count = sum(1 for l in out_tl3.splitlines() if l.strip() and 'hermes.exe' in l.lower()) - 1 if rc_tl3 == 0 else 0

report["checks"]["processes"] = {
    "load_percent": load,
    "node_count": max(0, node_count),
    "python_count": max(0, python_count),
    "hermes_count": max(0, hermes_count),
    "severity": "info"
}
total_agent = max(0, node_count) + max(0, python_count) + max(0, hermes_count)
if total_agent == 0:
    alerts.append("No Hermes-related agent processes found (node/python/hermes)")

# 4) Disk C:
rc, out, err = run_cmd("df -h /c/Users/hello")
disk_info = {"raw": out.strip(), "severity": "info", "status": "ok"}
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
            if (100 - used_pct) <= 10:
                alerts.append(f"Disk C: free space ({round(100 - used_pct, 1)}%) <= 10% threshold")
report["checks"]["disk"] = disk_info

# 5) Git
git_dir = "/c/Users/hello/alforaijboard-gh"
rc, out, err = run_cmd(f"cd {git_dir} && git status --porcelain")
git_status = "clean" if rc == 0 and not out.strip() else ("dirty" if rc == 0 else "error")
git_lines = [l.strip() for l in out.splitlines() if l.strip()] if rc == 0 else []
report["checks"]["git"] = {
    "status": git_status,
    "changes": git_lines,
    "change_count": len(git_lines),
    "severity": "info" if git_status == "clean" else "warning"
}
if git_status == "dirty":
    alerts.append(f"Git repo has {len(git_lines)} uncommitted change(s)")
    for gl in git_lines[:5]:
        warnings_list.append(f"  {gl}")
    if len(git_lines) > 5:
        warnings_list.append(f"  ... and {len(git_lines) - 5} more")

# Build human-readable report
human_lines = []
human_lines.append(f"🩺 System Health Report — {timestamp}")
human_lines.append(f"Host: DESKTOP-2U21BL4 | Project: alforaijboard")
human_lines.append("─" * 60)

# Docker
d = report["checks"]["docker"]
if d["status"] == "running":
    human_lines.append(f"🐳 Docker: OK — {d['container_count']} container(s) running")
    if d['containers']:
        human_lines.append(f"   {', '.join(d['containers'])}")
else:
    human_lines.append(f"🐳 Docker: DOWN — daemon not reachable")
    alerts.append("Docker daemon not running")

# RAM
r = report["checks"]["ram"]
status_icon = "✅" if r["status"] == "ok" else "⚠️"
human_lines.append(f"{status_icon} RAM: {r['free_mb']} MB free / {r['total_mb']} MB total ({round(r['free_mb']/r['total_mb']*100, 1)}%)")

# Processes
p = report["checks"]["processes"]
human_lines.append(f"📊 CPU Load: {p['load_percent']}%")
human_lines.append(f"   Processes: node={p['node_count']}, python={p['python_count']}, hermes={p['hermes_count']}")
if p['node_count'] == 0 and p['python_count'] == 0 and p['hermes_count'] == 0:
    human_lines.append("   ⚠️ No agent processes detected")

# Disk
disk = report["checks"]["disk"]
d_icon = "✅" if disk.get("status") == "ok" else "⚠️"
human_lines.append(f"{d_icon} Disk C:: {disk.get('free_gb', 'N/A')} GB free / {disk.get('total_gb', 'N/A')} GB total ({disk.get('free_pct', 'N/A')}% free)")

# Git
g = report["checks"]["git"]
g_icon = "✅" if g["status"] == "clean" else "⚠️"
human_lines.append(f"{g_icon} Git (alforaijboard): {g['status'].upper()} — {g['change_count']} change(s)")
if g['changes']:
    for gl in g['changes'][:5]:
        human_lines.append(f"   {gl}")
    if len(g['changes']) > 5:
        human_lines.append(f"   ... and {len(g['changes']) - 5} more")

human_lines.append("─" * 60)
if alerts:
    human_lines.append(f"🚨 {len(alerts)} ALERT(S):")
    for a in alerts:
        human_lines.append(f"   • {a}")
if warnings_list:
    human_lines.append(f"💡 {len(warnings_list)} note(s):")
    for w in warnings_list:
        human_lines.append(f"   • {w}")
if not alerts and not warnings_list:
    human_lines.append("✅ All systems nominal.")

human_lines.append(f"Timestamp: {timestamp}")
full_report = "\n".join(human_lines)

# Save to local history
report["human_report"] = full_report
report["alerts_count"] = len(alerts)
report["warnings_count"] = len(warnings_list)
report["overall"] = "ok" if not alerts else "needs_attention"

try:
    with open(history_file) as f:
        existing = json.load(f)
except Exception:
    existing = []
if not any(e.get("file_ts") == file_ts for e in existing):
    existing.append(report)
with open(history_file, "w") as f:
    json.dump(existing, f, indent=2, ensure_ascii=False)

# Push to Supabase
try:
    payload = {
        "timestamp": [timestamp],
        "report": [full_report],
        "alerts": [len(alerts)],
        "project": [PROJECT_ID],
        "overall": ["ok" if not alerts else "needs_attention"]
    }
    headers = {
        "Content-Type": "application/json",
        "apikey": ANON_KEY,
        "Authorization": f"Bearer {ANON_KEY}"
    }
    try:
        resp = requests.post(f"{SUPABASE_URL}/rest/v1/cron_results", json=payload, headers=headers, timeout=10)
        if resp.status_code in (200, 201):
            human_lines.append(f"\n📡 Supabase: Pushed to cron_results (HTTP {resp.status_code})")
        else:
            human_lines.append(f"\n📡 Supabase: Failed (HTTP {resp.status_code}) — {resp.text[:200]}")
    except Exception as e:
        print(f"[DB] Supabase push failed (non-fatal): {e}")
except Exception as e:
    print(f"[DB] Supabase push failed (non-fatal): {e}")

print(full_report)
