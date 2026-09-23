#!/usr/bin/env python3
"""Check .git real path from Python."""
import os

repo = '/c/Users/hello/alforaijboard-gh'
git_path = os.path.join(repo, '.git')

print(f"repo: {repo}")
print(f"repo exists: {os.path.exists(repo)}")
print(f"repo isdir: {os.path.isdir(repo)}")
print()
print(f".git path: {git_path}")
print(f".git exists: {os.path.exists(git_path)}")
print(f".git isdir: {os.path.isdir(git_path)}")
print(f".git isfile: {os.path.isfile(git_path)}")
print()

# Check realpath
try:
    real = os.path.realpath(git_path)
    print(f".git realpath: {real}")
    print(f"realpath exists: {os.path.exists(real)}")
    print(f"realpath isdir: {os.path.isdir(real)}")
except Exception as e:
    print(f"realpath error: {e}")

print()

# Check abspath
abs_path = os.path.abspath(git_path)
print(f".git abspath: {abs_path}")
print(f"abspath exists: {os.path.exists(abs_path)}")
print(f"abspath isdir: {os.path.isdir(abs_path)}")
print()

# List all items in repo dir that start with .
items = os.listdir(repo)
dot_items = [i for i in items if i.startswith('.')]
print(f"Dot items in repo: {dot_items}")

print()
# Check each dot item
for item in dot_items:
    full = os.path.join(repo, item)
    print(f"  {item}: exists={os.path.exists(full)} isdir={os.path.isdir(full)} isfile={os.path.isfile(full)}")
