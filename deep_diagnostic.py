#!/usr/bin/env python3
"""Deep diagnostic: why git fails via subprocess but works in terminal."""
import subprocess, os

repo_lin = '/c/Users/hello/alforaijboard-gh'
repo_win = 'C:\\Users\\hello\\alforaijboard-gh'

print("=" * 60)
print("DIAGNOSTIC: Why git fails from Python subprocess")
print("=" * 60)

# 1. Check what Python sees
print("\n1. Python os.listdir (current dir):")
for item in sorted(os.listdir('.')):
    if item.startswith('.git') or 'git' in item.lower():
        print(f"   {item}")

print("\n2. Python os.path.exists checks:")
for p in ['.git', os.path.join(repo_lin, '.git'), os.path.join(repo_win, '.git')]:
    print(f"   '{p}': exists={os.path.exists(p)} isdir={os.path.isdir(p)}")

print("\n3. subprocess ls -la .git (from current dir):")
r = subprocess.run(['ls', '-la', '.git'], capture_output=True, text=True)
print(f"   RC={r.returncode}")
print(f"   Output: {r.stdout[:300] if r.stdout else r.stderr[:300]}")

print("\n4. subprocess git status (cwd=repo_lin, env vars set):")
env = os.environ.copy()
env['GIT_DIR'] = os.path.join(repo_lin, '.git')
env['GIT_WORK_TREE'] = repo_lin
print(f"   GIT_DIR={env['GIT_DIR']!r}")
print(f"   GIT_WORK_TREE={env['GIT_WORK_TREE']!r}")
print(f"   cwd={repo_lin!r}")
r = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True, env=env, cwd=repo_lin)
print(f"   RC={r.returncode}")
print(f"   stdout: {r.stdout[:200] if r.stdout else '(empty)'}")
print(f"   stderr: {r.stderr[:200] if r.stderr else '(empty)'}")

print("\n5. Same but using shell=True with bash -c:")
shell_cmd = f'cd {repo_lin} && GIT_DIR="{os.path.join(repo_lin, ".git")}" GIT_WORK_TREE="{repo_lin}" git status --porcelain'
r = subprocess.run(['bash', '-c', shell_cmd], capture_output=True, text=True)
print(f"   RC={r.returncode}")
print(f"   stdout: {r.stdout[:200] if r.stdout else '(empty)'}")
print(f"   stderr: {r.stderr[:200] if r.stderr else '(empty)'}")

print("\n6. Using win32 git directly (no path conversion):")
env2 = os.environ.copy()
env2['GIT_DIR'] = os.path.join(repo_win, '.git')
env2['GIT_WORK_TREE'] = repo_win
print(f"   GIT_DIR={env2['GIT_DIR']!r}")
print(f"   GIT_WORK_TREE={env2['GIT_WORK_TREE']!r}")
r = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True, env=env2, cwd=repo_win)
print(f"   RC={r.returncode}")
print(f"   stdout: {r.stdout[:200] if r.stdout else '(empty)'}")
print(f"   stderr: {r.stderr[:200] if r.stderr else '(empty)'}")

print("\n7. Check if git sees different HOME/USERPROFILE:")
r = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True, cwd=repo_lin)
print(f"   Without env vars, cwd={repo_lin!r}:")
print(f"   RC={r.returncode}")
print(f"   stderr: {r.stderr[:200] if r.stderr else '(empty)'}")

print("\n8. Check GIT_PATH / GIT_EXEC_PATH:")
r = subprocess.run(['git', 'version', '--build-options'], capture_output=True, text=True)
print(f"   git build options: {r.stdout[:300] if r.stdout else r.stderr[:200]}")
