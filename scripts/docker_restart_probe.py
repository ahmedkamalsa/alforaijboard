import os, subprocess, time, json

# Try restarting Docker Desktop service on Windows
try:
    # Approach 1: PowerShell Start-Service com.docker.service
    cmd = ['powershell', '-NoProfile', '-Command',
           'Start-Service -Name com.docker.service -ErrorAction Stop; '
           'Start-Sleep 8; '
           'docker ps --format "{{.Names}}" 2>&1']
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    print('STDOUT:', out.stdout)
    print('STDERR:', out.stderr)
    print('RC:', out.returncode)
except Exception as e:
    print(f'ERROR: {e}')
