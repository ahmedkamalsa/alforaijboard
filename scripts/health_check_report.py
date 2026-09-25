import subprocess
import json

def run(cmd, timeout=30):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return r.stdout.strip(), r.returncode

stamp_kwt, _ = run(["powershell", "-NoProfile", "-Command",
    "Get-Date -Format 'yyyy-MM-dd HH:mm:ss'"])

report_path = "C:/Users/hello/alforaijboard-gh/_cron_health_latest.json"
with open(report_path) as f:
    raw = json.load(f)

# The canonical fields are in the top-level of _cron_health_latest.json
docker = raw.get("docker", "UNKNOWN")
ram_total_mb = raw.get("ram_total_mb")
ram_free_mb = raw.get("ram_free_mb")
ram_ok = raw.get("ram_ok", "no")
disk_total_gb = raw.get("disk_total_gb")
disk_free_gb = raw.get("disk_free_gb")
disk_used_pct = raw.get("disk_used_pct")
disk_warn = raw.get("disk_warn", "no")
hermes_agents = raw.get("hermes_agents", "")
git_uncommitted = raw.get("git_uncommitted", "clean")
git_modified_count = raw.get("git_modified_count", 0)
git_untracked_count = raw.get("git_untracked_count", 0)

# Local detail block is optional; pull from _local if present
local = raw.get("_local", {})
detail = {
    "docker_detail": local.get("docker_detail", ""),
    "ram_detail": local.get("ram_detail", ""),
    "agents_detail": local.get("agents_detail", ""),
    "disk_detail": local.get("disk_detail", ""),
    "git_detail": local.get("git_detail", ""),
    "overall": local.get("overall", "UNKNOWN"),
}

short = {
    "timestamp": stamp_kwt,
    "docker": docker,
    "ram_total_mb": ram_total_mb,
    "ram_free_mb": ram_free_mb,
    "ram_ok": ram_ok,
    "disk_total_gb": disk_total_gb,
    "disk_free_gb": disk_free_gb,
    "disk_used_pct": disk_used_pct,
    "disk_warn": disk_warn,
    "hermes_agents": hermes_agents,
    "git_uncommitted": git_uncommitted,
    "git_modified_count": git_modified_count,
    "git_untracked_count": git_untracked_count,
    "_local": detail,
}

# Write canonical short report back
with open("_cron_health_latest.json", "w") as f:
    json.dump(short, f, indent=2)

print(json.dumps(short, indent=2))
