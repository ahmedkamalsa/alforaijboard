#!/usr/bin/env python3
"""Run health check v3 and report results."""
import subprocess, sys, os

# Use the python from the venv if available
venv_python = r"C:\Users\hello\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe"
script = r"C:\Users\hello\alforaijboard-gh\health_check_v3.py"

if os.path.exists(venv_python):
    cmd = [venv_python, script]
else:
    cmd = [sys.executable, script]

print(f"Running: {' '.join(cmd)}")
result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
print(f"Exit: {result.returncode}")
