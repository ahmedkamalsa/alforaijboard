import subprocess
import json
import re
from datetime import datetime, timezone, timedelta

KWT = timezone(timedelta(hours=3))
HOST = "C:/Users/hello"
REPO = "C:/Users/hello/alforaijboard-gh"

def run(cmd, timeout=30, cwd=None):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, cwd=cwd)
    return r

def ram():
    """Use /proc/meminfo on Linux; on pure Windows fallback to ctypes/WMI via python."""
    r = run("cat /proc/meminfo 2>/dev/null | grep -E 'MemTotal|MemAvailable|MemFree'", timeout=15)
    if r.returncode == 0 and r.stdout.strip():
        total = mb(r.stdout, "MemTotal")
        avail = mb(r.stdout, "MemAvailable") or mb(r.stdout, "MemFree")
        if total and avail:
            return total, avail
    # Fallback: parse raw output directly when grep pattern returns empty
    r2 = run("cat /proc/meminfo 2>/dev/null", timeout=15)
    if r2.returncode == 0 and r2.stdout.strip():
        t = re.search(r"MemTotal:\s+(\d+)", r2.stdout)
        a = re.search(r"MemAvailable:\s+(\d+)", r2.stdout) or re.search(r"MemFree:\s+(\d+)", r2.stdout)
        if t and a:
            return int(t.group(1)) // 1024, int(a.group(1)) // 1024
    return None, None

def mb(text, key):
    m = re.search(rf"{re.escape(key)}:\s*(\d+)\s*kB", text)
    if m:
        return int(m.group(1)) // 1024
    return None

def disk():
    r = run(f"df -BM '{HOST}' 2>&1 | tail -1", timeout=15)
    if r.returncode != 0:
        return None, None, None
    m = re.search(r"(\d+)M\s+(\d+)M\s+(\d+)M\s+(\d+)%", r.stdout)
    if not m:
        m = re.search(r"(\d+)M\s+(\d+)M\s+(\d+)M\s+(\d+)%", r.stdout)
    if not m:
        m = re.search(r"(\d+)\s+(\d+)\s+(\d+)\s+(\d+)%", r.stdout)
    if m:
        total_mb = int(m.group(1))
        used_mb = int(m.group(2))
        avail_mb = int(m.group(3))
        free_gb = round(avail_mb / 1024.0, 2)
        total_gb = round(total_mb / 1024.0, 2)
        used_pct = int(m.group(4))
        return total_gb, free_gb, used_pct
    return None, None, None

def hermes():
    r = run("tasklist 2>&1 | grep -iE 'hermes'", timeout=15)
    if r.returncode != 0:
        return []
    lines = [l for l in r.stdout.splitlines() if l.strip() and "hermes" in l.lower()]
    return lines

def git():
    r = run(f"git status --short", timeout=30, cwd=REPO)
    if r.returncode != 0:
        return None
    modified = [l for l in r.stdout.splitlines() if l.strip().startswith("M ")]
    untracked = [l for l in r.stdout.splitlines() if l.strip().startswith("??")]
    return len(modified), len(untracked), modified, untracked

def main():
    ts = datetime.now(KWT).strftime("%Y-%m-%d %H:%M:%S")
    report = {"timestamp": ts}
    lines = []
    status = "OK"
    issues = []

    # Docker
    dr = run("docker ps 2>&1", timeout=30)
    if dr.returncode != 0:
        report["docker"] = "STOPPED"
        report["_local_docker_detail"] = "Docker daemon not reachable (pipe //./pipe/dockerDesktopLinuxEngine missing). لسه ما ينシャّط"
    else:
        report["docker"] = "OK"

    # RAM
    total = avail = None
    for i in range(3):
        r = run("cat /proc/meminfo 2>/dev/null", timeout=15)
        if r.returncode != 0 or not r.stdout.strip():
            continue
        t = re.search(r"MemTotal:\s+(\d+)", r.stdout)
        a = re.search(r"MemAvailable:\s+(\d+)", r.stdout) or re.search(r"MemFree:\s+(\d+)", r.stdout)
        if t and a:
            total = int(t.group(1)) // 1024
            avail = int(a.group(1)) // 1024
            break
        time.sleep(0.5)
    if total and avail:
        report["ram_total_mb"] = total
        report["ram_free_mb"] = avail
        report["ram_ok"] = "yes" if avail > 500 else "no"
        if report.get("ram_ok") == "yes":
            lines.append(f"RAM: طبيعي OK ({report.get('ram_free_mb')} ميجابايت حر من {report.get('ram_total_mb')} ميجابايت)")
        elif report.get("ram_ok") == "no":
            status = "WARN"
            issues.append(f"RAM أقل من 500 ميجابايت (حر {report.get('ram_free_mb')} من {report.get('ram_total_mb')})")
            lines.append(f"RAM: LOW ({report.get('ram_free_mb')} ميجابايت حر من {report.get('ram_total_mb')} ميجابايت)")
    else:
        report["ram_total_mb"] = None
        report["ram_free_mb"] = None
        report["ram_ok"] = "check"
        lines.append("RAM: لا متوفرة")

    # Hermes agents
    procs = hermes()
    report["hermes_agents"] = procs[0] if procs else "NOT_FOUND"

    # Disk
    tg, fg, up = disk()
    if tg and fg:
        report["disk_total_gb"] = tg
        report["disk_free_gb"] = fg
        report["disk_used_pct"] = up
        report["disk_warn"] = "yes" if (fg / tg) < 0.10 else "no"
    else:
        report["disk_total_gb"] = None
        report["disk_free_gb"] = None
        report["disk_warn"] = "check"

    # Git
    g = git()
    if g is None:
        report["git_uncommitted"] = "error"
    else:
        md, ut, mod_files, unt_files = g
        report["git_modified_count"] = md
        report["git_untracked_count"] = ut
        report["git_uncommitted"] = "unclean" if (md > 0 or ut > 0) else "clean"

    # Build readable Arabic text
    lines.append(f"تقرير الفحص الصحي - {ts} (توقيت الكويت)")
    lines.append("")
    if report.get("docker") == "STOPPED":
        status = "WARN"
        issues.append("Docker daemon متوقف")

    if report.get("hermes_agents") == "NOT_FOUND":
        status = "WARN"
        issues.append("عمليات Hermes مش لسعة")
    else:
        lines.append(f"Hermes: يعمل ({report.get('hermes_agents')})")

    if report.get("disk_warn") == "yes":
        status = "WARN"
        issues.append(f"مساحة القرص C: أقل من 10% ({report.get('disk_free_gb')} جيجابايت حر من {report.get('disk_total_gb')} جيجابايت)")

    if report.get("git_uncommitted") == "unclean":
        status = "WARN"
        issues.append(f"Git فيه {report.get('git_modified_count')} ملفات Modified + {report.get('git_untracked_count')} untracked")

    if status == "OK":
        lines.append("الحالة العامة: OK - لا مشاكل")
    else:
        lines.append(f"الحالة العامة: تحذير (WARN) - {len(issues)} مشاكل")
    if issues:
        lines.append("")
        lines.append("المشاكل:")
        for i, issue in enumerate(issues, 1):
            lines.append(f"  {i}) {issue}")

    lines.append("")
    lines.append("ملخص سريع:")
    lines.append(f"  Docker: {report.get('docker')}")
    if report.get("ram_ok") == "yes":
        lines.append(f"  RAM: OK ({report.get('ram_free_mb')} من {report.get('ram_total_mb')} ميجابايت)")
    elif report.get("ram_ok") == "no":
        lines.append(f"  RAM: LOW ({report.get('ram_free_mb')} من {report.get('ram_total_mb')} ميجابايت)")
    else:
        lines.append("RAM: لا متوفرة")

    lines.append(f"  العمليات: {'OK' if report.get('hermes_agents') != 'NOT_FOUND' else 'NOT_FOUND'}")
    if report.get('disk_warn') == 'yes':
        lines.append(f"  القرص: WARN ({report.get('disk_free_gb')} جيجابايت حر من {report.get('disk_total_gb')} جيجابايت)")
    elif report.get('disk_warn') == 'no':
        lines.append(f"  القرص: OK")
    else:
        lines.append("  القرص: لا متوفر")

    lines.append(f"  Git: {'DIRTY' if report.get('git_uncommitted') == 'unclean' else 'CLEAN'} {report.get('git_modified_count',0)} Modified, {report.get('git_untracked_count',0)} untracked")

    print("\n".join(lines))
    with open("_cron_health_latest.json", "w", encoding="utf-8") as f:
        updated = dict(report)
        updated["_local_docker_detail"] = report.get("_local_docker_detail", "")
        json.dump(updated, f, ensure_ascii=False, indent=2)
    print("\nSaved _cron_health_latest.json")


if __name__ == "__main__":
    main()
