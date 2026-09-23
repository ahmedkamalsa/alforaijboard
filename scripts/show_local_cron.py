#!/usr/bin/env python3
import json, os

path = "/c/Users/hello/alforaijboard-gh/cron_results_local.json"
if not os.path.exists(path):
    print("No local cron_results_local.json yet")
    exit(0)

with open(path) as f:
    rows = json.load(f)

print(f"Total local rows: {len(rows)}")
if rows:
    last = rows[0]
    overall = last.get("overall", last.get("status", "?"))
    created = last.get("timestamp", last.get("created_at", "?"))
    print(f"\n=== LATEST RUN ({created}) ===")
    print(f"Overall: {overall}")
    for key, val in last.items():
        if key in ("cron_id","host","timestamp","overall","status"):
            continue
        print(f"  {key}: {val}")
    
    # Filter for Docker failures
    docker_down = [r for r in rows if "Docker: DOWN" in str(r)]
    print(f"\nDocker DOWN count in local history: {len(docker_down)}")
    if docker_down:
        latest_down = docker_down[0].get("timestamp","") or docker_down[0].get("created_at","")
        oldest_down = docker_down[-1].get("timestamp","") or docker_down[-1].get("created_at","")
        print(f"  First: {oldest_down}")
        print(f"  Last:  {latest_down}")
        print(f"  Gap:   {latest_down[:10] if latest_down else '?'}")
