#!/usr/bin/env python3
"""Quick disk check: test wmic vs powershell vs shutil vs psutil."""
import subprocess, shutil, os

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return r.stdout.strip(), r.stderr.strip(), r.returncode

home = os.path.expanduser("~")
home_posix = home.replace("\\", "/")
print(f"Home: {home}")
print(f"Home POSIX: {home_posix}")

# 1. wmic
print("\n=== 1. wmic ===")
out, err, rc = run('wmic logicaldisk where "DeviceID=\\"C:\\"" get Size,FreeSpace /value')
print(f"rc={rc}, out=[{out}], err=[{err[:100] if err else 'none'}]")

# 2. shutil with raw string
print("\n=== 2. shutil via python file ===")
test_code = f'''
import shutil, os
p = r"{home}"
print(f"path: {{p}}")
d = shutil.disk_usage(p)
print(f"free={{d.free/1024**3:.1f}} total={{d.total/1024**3:.1f}} pct={{(d.free/d.total)*100:.1f}}")
'''
with open(r"C:\Users\hello\alforaijboard-gh\scripts\shutil_test.py", "w") as f:
    f.write(test_code)
out2, err2, rc2 = run("python3 /c/Users/hello/alforaijboard-gh/scripts/shutil_test.py")
print(f"rc={rc2}, out=[{out2}], err=[{err2[:100] if err2 else 'none'}]")

# 3. Check if C: path works
print("\n=== 3. Check C: directly ===")
out3, err3, rc3 = run(f"python3 -c \"import shutil; print(shutil.disk_usage(r'{home}'))\")")
print(f"rc={rc3}, out=[{out3}], err=[{err3[:100] if err3 else 'none'}]")

# 4. Just verify the path exists in python
print("\n=== 4. Path verification ===")
out4, err4, rc4 = run(f"python3 -c \"import os; p=r'{home}'; print(f'exists={{os.path.exists(p)}} isdir={{os.path.isdir(p)}}')\")")
print(f"rc={rc4}, out=[{out4}], err=[{err4[:100] if err4 else 'none'}]")

