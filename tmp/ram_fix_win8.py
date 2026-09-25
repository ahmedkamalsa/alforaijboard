import json, subprocess, sys, os, re

raw_path = "C:/Users/hello/AppData/Local/Temp/report_raw.json"
print("Looking for:", raw_path, "file exists:", os.path.exists(raw_path))

r = json.load(open(raw_path))
print("Loaded raw report:", r["timestamp"], "overall:", r["overall"])

# RAM — PowerShell to get free memory
ram_status = "FAIL"
ram_detail = r["checks"]["ram"]["detail"]

try:
    r2 = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "$os = Get-WmiObject Win32_OperatingSystem; "
         "Write-Output ('TOTAL:' + $os.TotalVisibleMemorySize + 'FREE:' + $os.FreePhysicalMemory)"],
        capture_output=True, text=True, timeout=15)
    print("PS rc:", r2.returncode)
    print("PS stdout:", repr(r2.stdout[:500]))
    if r2.returncode == 0:
        for line in r2.stdout.split("\n"):
            m = re.match(r"TOTAL:(\d+)FREE:(\d+)", line)
            if m:
                total_kb = int(m.group(1))
                free_kb = int(m.group(2))
                total_mb = total_kb / 1024
                free_mb = free_kb / 1024
                ram_status = "OK" if free_mb > 500 else "WARN"
                ram_detail = "Free: {}MB / Total: {}MB ({}% free) — threshold: 500MB".format(
                    round(free_mb), round(total_mb), round(free_mb/total_mb*100, 1))
                print("RAM via PS: avail={}MB total={}MB status={}".format(round(free_mb), round(total_mb), ram_status))
                break
        else:
            print("No TOTAL/FREE line in PS output")
    else:
        print("PS non-zero rc")
except Exception as e:
    print("RAM check exception:", str(e))

r["checks"]["ram"] = {"status": ram_status, "detail": ram_detail}
overall = "OK" if all(c["status"] == "OK" for c in r["checks"].values()) else "WARN"
r["overall"] = overall

print("=== FINAL REPORT ===")
print(json.dumps(r, indent=2, ensure_ascii=False))

out_path = "C:/Users/hello/AppData/Local/Temp/report_final.json"
with open(out_path, "w") as f:
    json.dump(r, f, indent=2, ensure_ascii=False)
print("Saved to", out_path)
