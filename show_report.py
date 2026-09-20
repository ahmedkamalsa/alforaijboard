#!/usr/bin/env python3
import json
d = json.load(open("/c/Users/hello/alforaijboard-gh/_cron_health_latest.json"))
print("TIMESTAMP:", d["timestamp_kt"])
print("OVERALL:", d["overall"], "| status:", d["status"])
print()
for k, v in d["checks"].items():
    print(f"[{k.upper()}] {v['status']} ({v['severity']})")
    print(f"  {v['details']}")
print()
print("docker_status:", d["docker_status"])
print("ram:", d["ram_free_mb"], "MB free /", d["ram_total_mb"], "MB total")
print("disk:", d["disk_free_gb"], "GB free /", d["disk_total_gb"], "GB total (", d["disk_free_pct"], "% free)")
print("agents:", d["agent_count"], "processes | PIDs:", d["agent_pids"])
print("git:", d["git_status"], "| modified:", d["git_modified"], "| untracked:", d["git_untracked_count"])
print()
print("ALERTS:", d.get("alerts", []))
print("WARNINGS:", d.get("warnings", []))
