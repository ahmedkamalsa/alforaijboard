#!/usr/bin/env python3
"""Append latest health report to cron_results_local.json history file."""
import json, datetime, os
latest = json.load(open("/c/Users/hello/alforaijboard-gh/_cron_health_latest.json", encoding="utf-8"))
history_path = "/c/Users/hello/alforaijboard-gh/cron_results_local.json"
history = []
if os.path.exists(history_path):
    with open(history_path, encoding="utf-8") as f:
        history = json.load(f)
    if not isinstance(history, list):
        history = [history]
new_entry = {
    "cron_id": "cron_health_%s" % datetime.datetime.now().strftime("%Y%m%d_%H%M"),
    "timestamp": latest.get("timestamp", ""),
    "timestamp_kt": latest.get("timestamp_kt", ""),
    "status": latest.get("status", "unknown"),
    "docker_running": latest.get("docker_running", False),
    "ram_free_mb": latest.get("ram_free_mb", 0),
    "ram_total_mb": latest.get("ram_total_mb", 0),
    "agent_count_python": latest.get("agent_count_python", 0),
    "agent_count_node": latest.get("agent_count_node", 0),
    "disk_free_gb": latest.get("disk_free_gb", 0),
    "disk_total_gb": latest.get("disk_total_gb", 0),
    "disk_free_pct": latest.get("disk_free_pct", 0),
    "git_modified_count": latest.get("git_modified_count", 0),
    "git_untracked_count": latest.get("git_untracked_count", 0),
    "git_status": latest.get("git_status", "unknown"),
    "alerts": latest.get("alerts", []),
    "warnings": latest.get("warnings", []),
}
history.append(new_entry)
with open(history_path, "w", encoding="utf-8") as f:
    json.dump(history, f, indent=2, ensure_ascii=False)
print("Saved to cron_results_local.json - entries: %d" % len(history))
