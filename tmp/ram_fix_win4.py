import json, subprocess, sys, os

raw_path = "C:/Users/hello/AppData/Local/Temp/report_raw.json"
print("Looking for:", raw_path, "file exists:", os.path.exists(raw_path))

r = json.load(open(raw_path))
print("Loaded raw report:", r["timestamp"], "overall:", r["overall"])

# RAM — try free -m first
ram_status = "FAIL"
ram_detail = r["checks"]["ram"]["detail"]

try:
    r2 = subprocess.run(["free", "-m"], capture_output=True, text=True, timeout=5)
    if r2.returncode == 0 and "Mem:" in r2.stdout:
        for line in r2.stdout.split("\n"):
            if line.startswith("Mem:"):
                parts = line.split()
                total_mb = int(parts[1])
                free_mb = int(parts[3]) if len(parts) > 3 else 0
                avail_mb = int(parts[6]) if len(parts) > 6 else free_mb
                ram_status = "OK" if avail_mb > 500 else "WARN"
                ram_detail = "Free: {}MB / Total: {}MB ({}% free) — threshold: 500MB".format(
                    avail_mb, total_mb, round(avail_mb/total_mb*100, 1))
                print("RAM via free -m: avail={}MB total={}MB status={}".format(avail_mb, total_mb, ram_status))
                break
        else:
            print("No Mem: line in free -m output")
    else:
        print("free -m failed: rc={} stderr={}".format(r2.returncode, r2.stderr[:200]))
except Exception as e:
    print("RAM check exception:", str(e))

r["checks"]["ram"] = {"status": ram_status, "detail": ram_detail}
overall = "OK" if all(c["status"] == "OK" for c in r["checks"].values()) else "WARN"
r["overall"] = overall

print("=== FINAL REPORT ===")
print(json.dumps(r, indent=2, ensure_ascii=False))

# Save to file
out_path = "C:/Users/hello/AppData/Local/Temp/report_final.json"
with open(out_path, "w") as f:
    json.dump(r, f, indent=2, ensure_ascii=False)
print("Saved to", out_path)
