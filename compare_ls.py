#!/usr/bin/env python3
"""Check all dot files in repo and verify .git via os.listdir."""
import os, subprocess

repo = '/c/Users/hello/alforaijboard-gh'

print(f"=== All items in {repo} ===")
for item in sorted(os.listdir(repo)):
    full = os.path.join(repo, item)
    is_dir = os.path.isdir(full)
    marker = '/' if is_dir else ''
    size = ''
    if os.path.isfile(full):
        size = f' ({os.path.getsize(full)} bytes)'
    print(f'  {item}{marker}{size}')

print()
print("=== Hidden items (.*) ===")
for item in sorted(os.listdir(repo)):
    if item.startswith('.'):
        full = os.path.join(repo, item)
        is_dir = os.path.isdir(full)
        marker = 'DIR' if is_dir else 'FILE'
        print(f'  {item} -> {marker}')

print()
print("=== os.listdir vs subprocess ls comparison ===")
# Python sees:
py_items = set(os.listdir(repo))
print(f"Python sees {len(py_items)} items")

# subprocess ls
r = subprocess.run(['ls', '-1', repo], capture_output=True, text=True)
sub_items = set(line.strip() for line in r.stdout.splitlines() if line.strip())
print(f"subprocess ls sees {len(sub_items)} items")

only_py = py_items - sub_items
only_sub = sub_items - py_items
if only_py:
    print(f"Only Python sees: {only_py}")
if only_sub:
    print(f"Only subprocess sees: {only_sub}")
if not only_py and not only_sub:
    print("Both see the same items")

print()
print("=== Checking .git via subprocess ls explicitly ===")
r = subprocess.run(['ls', '-la', os.path.join(repo, '.git')], capture_output=True, text=True)
print(f"ls -la .git RC={r.returncode}")
print(r.stdout[:300] if r.stdout else r.stderr[:300])
