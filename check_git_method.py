#!/usr/bin/env python3
"""Check git status using multiple methods."""
import subprocess

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return r.returncode, r.stdout.strip(), r.stderr.strip()

print("=== Method 1: git --git-dir + --work-tree ===")
rc, out, err = run('cd /c/Users/hello/alforaijboard-gh && git --git-dir=.git --work-tree=. status --porcelain')
print(f'RC={rc}')
print(out[:300] if out else err[:300])

print("\n=== Method 2: git -C . ===")
rc, out, err = run('git -C /c/Users/hello/alforaijboard-gh status --porcelain')
print(f'RC={rc}')
print(out[:300] if out else err[:300])

print("\n=== Method 3: direct git status in dir ===")
rc, out, err = run('cd /c/Users/hello/alforaijboard-gh && git status --porcelain')
print(f'RC={rc}')
print(out[:300] if out else err[:300])

print("\n=== .git type ===")
rc, out, err = run('test -f /c/Users/hello/alforaijboard-gh/.git && echo "FILE" || echo "DIR"')
print(out)
