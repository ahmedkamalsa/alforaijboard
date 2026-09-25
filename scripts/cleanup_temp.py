#!/usr/bin/env python3
"""Clean up temp files from health check run."""
import os, glob

base = "/c/Users/hello/alforaijboard-gh"
for pat in ["_temp_*.py", "_health_*.py", "_run_*.py", "append_cron_*.py",
            "run_health_*.py", "debug_*.py", "flush_*.py", "test_*.py",
            "health_check_*.py", "health_report_*.py", "health_*.py",
            "push_*.py", "show_*.py", "scripts/cleanup_*.py"]:
    for f in glob.glob(os.path.join(base, pat)):
        if f.endswith("/scripts/cleanup_temp.py"):
            continue  # keep self
        try:
            os.remove(f)
            print("removed:", f.replace(base + "/", ""))
        except Exception as e:
            print("failed to remove", f, e)

print("cleanup done")
