#!/usr/bin/env python3
"""Pretty-print the health check JSON to a readable report."""
import json, os

path = "C:/Users/hello/alforaijboard-gh/_cron_health_latest.json"
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

print("=" * 70)
print("ALFORAIJBOARD SYSTEM HEALTH REPORT")
print(f"Time (UTC): {data['timestamp']}")
print("=" * 70)
print()

checks = [
    ("DOCKER", "docker"),
    ("RAM", "ram"),
    ("DISK C:", "disk_c"),
    ("GIT", "git"),
]
for label, key in checks:
    d = data.get(key, {})
    print(f"[{label}]")
    if key == "docker":
        status = d.get("status", "?")
        print(f"  Status: {status}")
        if status == "OK":
            print(f"  Containers: {d.get('count', 0)} running")
        else:
            print(f"  Error: {d.get('error', '?')[:120]}")
    elif key == "ram":
        print(f"  Free: {d.get('free_mb', '?')} MB / {d.get('total_gb', '?')} GB total ({d.get('pct', '?')}%)")
        print(f"  Status: {d.get('status', 'OK')}")
    elif key == "disk_c":
        fp = d.get("free_pct", 0)
        print(f"  Free: {d.get('free_gb', '?')} GB ({fp}%) / {d.get('total_gb', '?')} GB total")
        print(f"  Status: {'OK' if fp > 10 else 'CRITICAL'}")
    elif key == "git":
        print(f"  Status: {d.get('status', '?')} ({d.get('count', 0)} uncommitted)")
        if d.get("count", 0) > 0:
            print(f"  First 10 changes:")
            for c in d.get("changes", [])[:10]:
                print(f"    {c}")
            if d["count"] > 10:
                print(f"    ... and {d['count'] - 10} more")
    print()

print("=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Alerts: {len(data['alerts'])} | Warnings: {len(data['warnings'])} | All OK: {data['all_ok']}")
if data["alerts"]:
    print()
    print("ALERTS:")
    for a in data["alerts"]:
        print(f"  ! {a}")
if data["warnings"]:
    print()
    print("WARNINGS:")
    for w in data["warnings"]:
        print(f"  ~ {w}")
print()
print("Local report: _cron_health_latest.json")
