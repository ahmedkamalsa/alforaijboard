#!/usr/bin/env python3
"""Read latest health report from _cron_health_latest.json and print to stdout."""
import json, sys
r = json.load(open("/c/Users/hello/alforaijboard-gh/_cron_health_latest.json", encoding="utf-8"))
print("HEALTH REPORT —", r.get("timestamp_kt", r.get("timestamp", "unknown")))
print("Status:", r.get("status", "unknown"))
print("Docker:", "running" if r.get("docker_running") else "DOWN")
print("RAM: %.0f MB free / %.0f MB total" % (r.get("ram_free_mb", 0), r.get("ram_total_mb", 0)))
print("Agents: Python %d, Node %d" % (r.get("agent_count_python", 0), r.get("agent_count_node", 0)))
print("Disk: %.1f GB free / %.0f GB total (%.1f%%)" % (r.get("disk_free_gb", 0), r.get("disk_total_gb", 0), r.get("disk_free_pct", 0)))
print("Git:", r.get("git_status", "unknown"), "(modified:", r.get("git_modified_count", 0), "untracked:", r.get("git_untracked_count", 0), ")")
print()
print("Alerts:")
for a in r.get("alerts", []):
    print("  !", a)
print()
print("Warnings:")
for w in r.get("warnings", []):
    print("  ~", w)
print()
print("Full report:")
print(r.get("report", ""))
