#!/usr/bin/env python3
"""Debug: test disk checks with proper escaping."""
import subprocess

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return r.stdout.strip(), r.stderr.strip(), r.returncode

# Test 1: wmic with proper filter
print("=== 1. wmic logicaldisk ===")
out, err, rc = run('wmic logicaldisk where "DeviceID=\\\"C:\\\"" get Size,FreeSpace /value')
print(f"rc={rc}")
print(f"out: [{out}]")
print(f"err: [{err[:200] if err else 'none'}]")

# Parse
size_bytes = free_bytes = None
for line in out.split("\n"):
    line = line.strip()
    if "Size=" in line:
        try: size_bytes = int(line.split("=")[1].strip())
        except: pass
    if "FreeSpace=" in line:
        try: free_bytes = int(line.split("=")[1].strip())
        except: pass

if size_bytes and free_bytes:
    total_gb = size_bytes / (1024**3)
    free_gb = free_bytes / (1024**3)
    free_pct = (free_bytes / size_bytes) * 100
    print(f"Parsed: free={free_gb:.1f} GB ({free_pct:.1f}%) / total={total_gb:.1f} GB")
else:
    print(f"Parse failed: size={size_bytes}, free={free_bytes}")

# Test 2: python shutil with proper path
print("\n=== 2. python3 shutil ===")
out2, err2, rc2 = run('python3 -c "import shutil; d=shutil.disk_usage(r\"/c/Users/hello\"); print(f\"free={d.free/1024**3:.1f} total={d.total/1024**3:.1f} pct={(d.free/d.total)*100:.1f}\")"')
print(f"rc={rc2}")
print(f"out: [{out2}]")
print(f"err: [{err2[:200] if err2 else 'none'}]")

# Test 3: python3 psutil
print("\n=== 3. python3 psutil ===")
out3, err3, rc3 = run('python3 -c "import psutil; v=psutil.disk_usage(r\"/c/Users/hello\"); print(f\"free={v.free/1024**3:.1f} total={v.total/1024**3:.1f} pct={v.percent:.1f}\")"')
print(f"rc={rc3}")
print(f"out: [{out3}]")
print(f"err: [{err3[:200] if err3 else 'none'}]")
