import subprocess
import json

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return r.stdout.strip(), r.returncode

out, rc = run(["powershell", "-NoProfile", "-Command",
    "Get-CimInstance Win32_OperatingSystem | Select-Object FreePhysicalMemory,TotalVisibleMemorySize | Format-List"])
print(out)
