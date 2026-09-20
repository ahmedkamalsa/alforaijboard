#!/usr/bin/env python3
"""Print the latest health report in readable form."""
import json
d = json.load(open("/c/Users/hello/alforaijboard-gh/cron_results_latest.json"))
print("═══════════════════════════════════════════════")
print(f"HEALTH REPORT — {d['timestamp_kt']}")
print(f"Host: {d['host']} | Overall: {d['overall']} | Status: {d['status'].upper()}")
print("═══════════════════════════════════════════════")
for k, v in d["checks"].items():
    icon = {"RUNNING":"✓","STOPPED":"✗","OK":"✓","LOW":"⚠","WARNING":"⚠","CLEAN":"✓","DIRTY":"⚠","NONE":"✗"}.get(v["status"], "?")
    print(f"  [{icon}] {k.upper():8s} {v['status']:10s} ({v['severity']:5s}) — {v['details']}")
print("───────────────────────────────────────────────")
print(f" Docker: {d['docker_status']}")
print(f" RAM:    {d['ram_free_mb']} MB free / {d['ram_total_mb']} MB total")
print(f" Disk:   {d['disk_free_gb']} GB free / {d['disk_total_gb']} GB total ({d['disk_free_pct']}% free)")
print(f" Agents: {d['agent_count']} processes | PIDs: {d['agent_pids']}")
print(f" Git:    {d['git_status']} | modified: {d['git_modified']} | untracked: {d['git_untracked_count']}")
print("───────────────────────────────────────────────")
print(f" ALERTS ({len(d.get('alerts',[]))}): {d.get('alerts',[])}")
print(f" WARNINGS ({len(d.get('warnings',[]))}): {d.get('warnings',[])}")
print("═══════════════════════════════════════════════")
