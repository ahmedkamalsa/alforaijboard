import subprocess
import json

def run(cmd, timeout=30):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return r.stdout.strip(), r.returncode

stamp_kwt, _ = run(["powershell", "-NoProfile", "-Command",
    "Get-Date -Format 'yyyy-MM-dd HH:mm:ss'"])

report_path = "C:/Users/hello/alforaijboard-gh/_cron_health_latest.json"
with open(report_path) as f:
    data = json.load(f)

# Build short fields directly here (no dependency on upstream format assumptions)
short = {
    "timestamp_kwt": stamp_kwt,
    "docker": data.get("_local", {}).get("docker", "UNKNOWN"),
    "ram_ok": "yes" if data.get("_local", {}).get("ram") == "OK" else "no",
    "ram_free_mb": data.get("_local", {}).get("ram_detail", ""),
    "agents_ok": "yes" if data.get("_local", {}).get("agents") == "OK" else "no",
    "agents_detail": data.get("_local", {}).get("agents_detail", ""),
    "disk_warn": data.get("_local", {}).get("disk_warn", "no"),
    "disk_detail": data.get("_local", {}).get("disk_detail", ""),
    "git_uncommitted": "unclean" if data.get("_local", {}).get("git") == "UNCLEAN" else "clean",
    "git_detail": data.get("_local", {}).get("git_detail", ""),
    "overall": data.get("_local", {}).get("overall", "UNKNOWN"),
}

with open("_cron_health_latest.json", "w") as f:
    json.dump(short, f, indent=2)

print(json.dumps(short, indent=2))
