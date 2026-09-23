#!/usr/bin/env python3
"""Check alforaijboard-gh directory from different angles."""
import os, subprocess

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return r.returncode, r.stdout.strip(), r.stderr.strip()

path = '/c/Users/hello/alforaijboard-gh'

print(f"Path exists: {os.path.exists(path)}")
print(f"Path is dir: {os.path.isdir(path)}")
print()

# List top-level items
if os.path.isdir(path):
    items = sorted(os.listdir(path))
    print(f"Contents ({len(items)} items):")
    for item in items:
        full = os.path.join(path, item)
        is_dir = os.path.isdir(full)
        marker = '/' if is_dir else ''
        print(f"  {item}{marker}")
    print()

# Check for .git in different forms
for suffix in ['', '.git', '/.git']:
    p = path + suffix
    print(f"'{p}' exists={os.path.exists(p)} isdir={os.path.isdir(p)} isfile={os.path.isfile(p)}")

print()

# Also check parent
parent = '/c/Users/hello'
if os.path.isdir(parent):
    kids = sorted(os.listdir(parent))
    print(f"User home has {len(kids)} items. alforaijboard-gh related:")
    for k in kids:
        if 'alfora' in k.lower() or 'git' in k.lower() or 'board' in k.lower():
            full = os.path.join(parent, k)
            print(f"  {k} -> exists={os.path.exists(full)} isdir={os.path.isdir(full)}")

print()

# Try to find any .git directory in user home
rc, out, err = run('find /c/Users/hello -maxdepth 3 -name ".git" -type d 2>/dev/null | head -10')
print(f"Found .git dirs:\n{out}")
