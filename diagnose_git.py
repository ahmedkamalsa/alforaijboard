#!/usr/bin/env python3
import subprocess, shutil, os

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return r.returncode, r.stdout.strip(), r.stderr.strip()

print("Python:", shutil.which('python3'))
print("Git:", shutil.which('git'))
print()

# Try git from Python directly
import git as git_module
print("GitPython version:", git_module.__version__ if hasattr(git_module, '__version__') else "unknown")

# Try cloning the repo fresh to test git
print("\n=== Testing git clone ===")
rc, out, err = run('cd /c/Users/hello/AppData/Local/hermes/cache/scratch && git clone https://github.com/ahmedkamalsa/alforaijboard.git test_clone 2>&1')
print(f'Clone RC={rc}')
print(out[:200] if out else err[:200])
