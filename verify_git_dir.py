#!/usr/bin/env python3
import os, subprocess

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return r.returncode, r.stdout.strip(), r.stderr.strip()

path = '/c/Users/hello/alforaijboard-gh'
git_path = os.path.join(path, '.git')

print(f".git exists: {os.path.exists(git_path)}")
print(f".git is dir: {os.path.isdir(git_path)}")
print(f".git is file: {os.path.isfile(git_path)}")
print()

# List .git contents
if os.path.isdir(git_path):
    items = os.listdir(git_path)
    print(f".git contains {len(items)} items:")
    for item in sorted(items)[:20]:
        print(f"  {item}")
    if len(items) > 20:
        print(f"  ... and {len(items) - 20} more")

print()

# Try git status one more time with explicit paths
rc, out, err = run(f'cd {path} && git --git-dir="{git_path}" --work-tree="{path}" status --porcelain 2>&1')
print(f"git --git-dir status RC={rc}")
print(out[:300] if out else err[:300])

# Check if it's a submodule pointer file
if os.path.isfile(git_path):
    with open(git_path) as f:
        print(f"\n.git file content: {f.read()}")
