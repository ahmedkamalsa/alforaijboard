#!/usr/bin/env python3
"""Debug script to check health report structure"""
import json

with open("/c/Users/hello/alforaijboard-gh/_cron_health_latest.json", "r") as f:
    data = json.load(f)

print("Top-level keys:", list(data.keys()))
print("Checks keys:", list(data.get("checks", {}).keys()))
print("Full data:", json.dumps(data, indent=2))
