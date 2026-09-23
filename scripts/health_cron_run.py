#!/usr/bin/env python3
"""Full health check — Docker, RAM, agents, disk, Git. Hourly cron for alforaijboard."""

import os, json, http.client, socket, subprocess, datetime
import psutil

socket.setdefaulttimeout(10)
HOST = "bwspcsiazbwrrxpgoldx.supabase.co"
REPO = "C:/Users/hello/alforaijboard-gh"
REPORT_FILE = os.path.join(REPO, "_cron_health_latest.json")
SR_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

print("=" * 70)
print("SYSTEM HEALTH CHECK — alforaijboard")
print(f"Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Key available: SUPABASE_SERVICE_KEY ({len(SR_KEY)} chars)")
print("=" * 70)
print()

REPORT_LINES = []
ALERTS = []
WARNINGS = []

def report(line):
    REPORT_LINES.append(line)
    print(line)

def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def run(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return r.returncode, r.stdout, r.stderr
    except Exception as e:
        return -1, "", str(e)

# ── 1. Docker ──
rc, out, err = run(["docker", "ps", "--format", "{{.Names}}"])
if rc == 0 and out.strip():
    containers = [c.strip() for c in out.strip().split("\n") if c.strip()]
    report(f"[DOCKER] OK — {len(containers)} container(s): {', '.join(containers)}")
    if not containers:
        WARNINGS.append("No containers running (daemon OK)")
elif rc == 0:
    report("[DOCKER] OK — daemon running, no containers")
else:
    msg = f"[DOCKER] DOWN — {err.strip()}"
    report(msg)
    ALERTS.append(msg)
    report("[DOCKER] Docker Desktop requires interactive restart (login needed on Windows)")

# ── 2. RAM ──
try:
    mem = psutil.virtual_memory()
    free_mb = mem.available / (1024 * 1024)
    total_mb = mem.total / (1024 * 1024)
    status = "OK" if free_mb > 500 else "LOW"
    report(f"[RAM] {status} — {free_mb:.0f} MB free / {total_mb:.0f} MB total ({free_mb/total_mb*100:.1f}%)")
    if free_mb <= 500:
        ALERTS.append(f"RAM free ({free_mb:.0f} MB) <= 500 MB threshold")
except Exception as e:
    report(f"[RAM] ERROR — {e}")
    ALERTS.append(f"RAM check failed: {e}")

# ── 3. Hermes agents ──
try:
    rc, out, err = run(["pgrep", "-af", "hermes"])
    agent_lines = [l.strip() for l in out.strip().split("\n") if l.strip()] if rc == 0 else []
    if agent_lines:
        report(f"[AGENTS] OK — {len(agent_lines)} Hermes process(es):")
        for line in agent_lines[:10]:
            pid, *rest = line.split()
            report(f"  PID={pid} {' '.join(rest[:4])}")
    else:
        rc2, out2, err2 = run(["pgrep", "-af", "node"])
        node_lines = [l.strip() for l in out2.strip().split("\n") if l.strip()] if rc2 == 0 else []
        rc3, out3, err3 = run(["pgrep", "-af", "python"])
        py_lines = [l.strip() for l in out3.strip().split("\n") if l.strip()] if rc3 == 0 else []
        total = len(node_lines) + len(py_lines)
        if total > 0:
            report(f"[AGENTS] OK — {total} Node/Python process(es) (Hermes may be among them)")
            combined = node_lines + py_lines
            for line in combined[:10]:
                pid, *rest = line.split()
                report(f"  PID={pid} {' '.join(rest[:4])}")
        else:
            report("[AGENTS] None detected — Hermes cron is running but no child processes found (expected for single-run cron)")
            WARNINGS.append("No persistent Hermes agent processes — this is a cron execution, not a daemon")
except Exception as e:
    report(f"[AGENTS] ERROR — {e}")
    ALERTS.append(f"Agent check failed: {e}")

# ── 4. Disk C: ──
try:
    rc, out, err = run(["df", "-h", "C:/Users/hello"])
    if rc == 0:
        lines = [l.strip() for l in out.strip().split("\n") if l.strip()]
        if len(lines) >= 2:
            parts = lines[1].split()
            if len(parts) >= 5:
                free_pct = float(parts[4].replace("%", ""))
                status = "OK" if free_pct > 10 else ("LOW" if free_pct > 5 else "CRITICAL")
                report(f"[DISK C:] {status} — {parts[3]} free ({parts[4]}) / {parts[1]} total")
                if free_pct <= 10:
                    ALERTS.append(f"Disk C: free space ({free_pct}%) <= 10% threshold")
            else:
                report(f"[DISK] Parse issue: {lines[1]}")
        else:
            report("[DISK] Unexpected df output")
    else:
        report(f"[DISK] df failed: {err.strip()}")
        ALERTS.append(f"Disk check failed: {err.strip()}")
except Exception as e:
    report(f"[DISK] ERROR — {e}")
    ALERTS.append(f"Disk check failed: {e}")

# ── 5. Git alforaijboard ──
git_rc = None
git_dirty = []
try:
    rc, out, err = run(["git", "status", "--porcelain"])
    git_rc = rc
    if rc == 0:
        git_dirty = [l.strip() for l in out.strip().split("\n") if l.strip()]
        if git_dirty:
            report(f"[GIT] DIRTY — {len(git_dirty)} uncommitted change(s):")
            for d in git_dirty[:10]:
                report(f"  {d}")
            if len(git_dirty) > 10:
                report(f"  ... and {len(git_dirty) - 10} more")
            ALERTS.append(f"Git repo has {len(git_dirty)} uncommitted change(s)")
        else:
            report("[GIT] CLEAN — no uncommitted changes")
    else:
        report(f"[GIT] ERROR — {err.strip()}")
        ALERTS.append(f"Git check failed: {err.strip()}")
except Exception as e:
    report(f"[GIT] ERROR — {e}")
    ALERTS.append(f"Git check failed: {e}")

# ── Summary ──
print()
if ALERTS or WARNINGS:
    total = len(ALERTS) + len(WARNINGS)
    report(f"!!! {total} ISSUE(S): {len(ALERTS)} alert(s), {len(WARNINGS)} warning(s)")
    for a in ALERTS:
        report(f"  ! {a}")
    for w in WARNINGS:
        report(f"  ~ {w}")
else:
    report("All systems nominal.")

# ── Build report JSON ──
report_text = "\n".join(REPORT_LINES)
status_val = "error" if ALERTS else ("warning" if WARNINGS else "success")

checks = {
    "docker": "OK" if rc == 0 else "DOWN",
    "ram": f"{free_mb:.0f} MB free / {total_mb:.0f} MB total" if 'free_mb' in dir() else "ERROR",
    "disk_c": f"{free_pct:.1f}% free" if 'free_pct' in dir() else "ERROR",
    "agents": f"{len(agent_lines)} processes" if 'agent_lines' in dir() and agent_lines else ("node/py processes" if 'total' in dir() else "none"),
    "git": f"{len(git_dirty)} uncommitted" if git_dirty else "CLEAN",
}

report_data = {
    "timestamp": now_iso(),
    "timestamp_kt": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3))).strftime("%Y-%m-%d %H:%M UTC+03:00 (Kuwait Time)"),
    "report": report_text,
    "alerts": ALERTS,
    "warnings": WARNINGS,
    "status": status_val,
    "checks": checks,
}

with open(REPORT_FILE, "w", encoding="utf-8") as f:
    json.dump(report_data, f, indent=2, ensure_ascii=False)
print(f"\nLocal report saved: {REPORT_FILE}")

# ── Push to Supabase ──
if len(SR_KEY) > 10:
    now = datetime.datetime.now(datetime.timezone.utc)
    name = f"health_check_{now.strftime('%Y%m%d_%H%M')}"

    if ALERTS:
        msg_status = "error"
        lines = ["ALERTS:"] + [f"  ! {a}" for a in ALERTS]
        if WARNINGS:
            lines.append("")
            lines.append("WARNINGS:")
            lines.extend(f"  ~ {w}" for w in WARNINGS)
        message = "\n".join(lines)
    else:
        msg_status = "success"
        message = report_text

    payload_dict = {
        "name": name,
        "status": msg_status,
        "message": message,
        "duration_ms": None,
        "records_affected": None,
    }
    payload = json.dumps(payload_dict).encode()

    conn = http.client.HTTPSConnection(HOST, timeout=10)
    conn.request("POST", "/rest/v1/cron_results", body=payload, headers={
        "Content-Type": "application/json",
        "apikey": SR_KEY,
        "Authorization": f"Bearer {SR_KEY}",
    })
    resp = conn.getresponse()
    body = resp.read().decode("utf-8")
    http_status = resp.status
    conn.close()

    print(f"\n[DB] Supabase push:")
    print(f"     HTTP {http_status}")
    if http_status in (200, 201):
        try:
            inserted = json.loads(body)
            print(f"     ✓ Inserted id={inserted.get('id')} | name={inserted.get('name')} | status={inserted.get('status')}")
        except:
            print(f"     ✓ Success — {body[:100]}")
    else:
        print(f"     ✗ Failed: {body[:200]}")
else:
    print(f"\n[DB] SUPABASE_SERVICE_KEY not available — report not pushed to Supabase")

print()
print("=" * 70)
print("END OF HEALTH CHECK")
print("=" * 70)
