#!/usr/bin/env python3
"""Test git from Python subprocess directly."""
import subprocess, os

repo = '/c/Users/hello/alforaijboard-gh'
env = os.environ.copy()
env['GIT_DIR'] = os.path.join(repo, '.git')
env['GIT_WORK_TREE'] = repo

print("=== Test 1: git status --porcelain ===")
r = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True, env=env, cwd=repo)
print(f'RC={r.returncode}')
print(f'stdout: {r.stdout[:200]}')
print(f'stderr: {r.stderr[:200]}')

print("\n=== Test 2: git rev-parse --git-dir ===")
r = subprocess.run(['git', 'rev-parse', '--git-dir'], capture_output=True, text=True, env=env, cwd=repo)
print(f'RC={r.returncode}')
print(f'stdout: {r.stdout[:200]}')
print(f'stderr: {r.stderr[:200]}')

print("\n=== Test 3: git rev-parse --show-toplevel ===")
r = subprocess.run(['git', 'rev-parse', '--show-toplevel'], capture_output=True, text=True, env=env, cwd=repo)
print(f'RC={r.returncode}')
print(f'stdout: {r.stdout[:200]}')
print(f'stderr: {r.stderr[:200]}')

print("\n=== Test 4: Check env vars ===")
print(f'GIT_DIR={env.get("GIT_DIR")}')
print(f'GIT_WORK_TREE={env.get("GIT_WORK_TREE")}')
print(f'cwd={repo}')
print(f'.git exists={os.path.exists(os.path.join(repo, ".git"))}')
print(f'.git is dir={os.path.isdir(os.path.join(repo, ".git"))}')

print("\n=== Test 5: git version ===")
r = subprocess.run(['git', '--version'], capture_output=True, text=True)
print(f'git version: {r.stdout.strip()}')
