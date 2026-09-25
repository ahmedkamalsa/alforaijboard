import json, subprocess

raw_path = "C:/Users/hello/AppData/Local/Temp/report_raw.json"
print("Looking for:", raw_path)

r = json.load(open(raw_path))

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
            break
    else:
        ram_status = "FAIL"
        ram_detail = r["checks"]["ram"]["detail"]
else:
    ram_status = "FAIL"
    ram_detail = r["checks"]["ram"]["detail"] + " (free -m error: " + r2.stderr.strip() + ")"

r["checks"]["ram"] = {"status": ram_status, "detail": ram_detail}
overall = "OK" if all(c["status"] == "OK" for c in r["checks"].values()) else "WARN"
r["overall"] = overall
print(json.dumps(r, indent=2, ensure_ascii=False))
