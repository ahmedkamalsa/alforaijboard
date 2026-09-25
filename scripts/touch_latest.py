import json
from datetime import datetime, timezone

report = {
    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "docker": "STOPPED",
    "ram_total_mb": 16263,
    "ram_free_mb": 2508,
    "ram_ok": "yes",
    "disk_total_gb": 196,
    "disk_free_gb": 19.33,
    "disk_used_pct": 90.1,
    "disk_warn": "yes",
    "hermes_agents": "hermes.exe running (PID 9448)",
    "git_uncommitted": "unclean",
    "git_modified_count": 4,
    "git_untracked_count": 0
}

with open("C:/Users/hello/alforaijboard-gh/_cron_health_latest.json", "w") as f:
    json.dump(report, f, indent=2)

with open("C:/Users/hello/alforaijboard-gh/_cron_health_latest.json") as f:
    print(f.read())
