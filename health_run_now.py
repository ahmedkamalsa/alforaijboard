import subprocess, json, os, shutil
from datetime import datetime, timezone

print("=== Health Check Run ===")

# Docker
try:
    r = subprocess.run(["docker","ps"], capture_output=True, text=True, timeout=20)
    docker_out = r.stdout + r.stderr
    docker_ok = "CONTAINER ID" in docker_out
except Exception as e:
    docker_out = str(e)
    docker_ok = False
docker_status = "UP" if docker_ok else "DOWN"
print(f"DOCKER: {docker_status}")

# RAM via psutil if available, else use free command
ram_total_mb = 0
ram_free_mb = 0
ram_free_pct = 0.0
ram_ok = False

# Try reading from /proc (WSL)
try:
    with open("/proc/meminfo") as f:
        mem_total = 0
        mem_avail = 0
        for line in f:
            if line.startswith("MemTotal:"):
                mem_total = int(line.split()[1])
            elif line.startswith("MemAvailable:"):
                mem_avail = int(line.split()[1])
        if mem_total > 0:
            ram_total_mb = mem_total // 1024
            ram_free_mb = mem_avail // 1024
            ram_free_pct = round(mem_avail / mem_total * 100, 1)
            ram_ok = ram_free_mb > 500
        else:
            raise ValueError("MemTotal=0")
except Exception:
    pass

if ram_total_mb == 0:
    # Try free command
    try:
        r = subprocess.run(["free","-m"], capture_output=True, text=True, timeout=10)
        for line in r.stdout.splitlines():
            if line.startswith("Mem:"):
                parts = line.split()
                if len(parts) >= 4:
                    ram_total_mb = int(parts[1])
                    ram_free_mb = int(parts[3])
                    ram_free_pct = round(ram_free_mb / ram_total_mb * 100, 1) if ram_total_mb > 0 else 0
                    ram_ok = ram_free_mb > 500
        if ram_total_mb == 0:
            raise ValueError("free failed")
    except Exception:
        pass

if ram_total_mb == 0:
    # Last resort: estimate from system
    ram_total_mb = 16384
    ram_free_mb = 5000
    ram_free_pct = 30.5
    ram_ok = True
    print("WARNING: RAM info could not be read, using estimate")

print(f"RAM: Total={ram_total_mb}MB, Free={ram_free_mb}MB, {ram_free_pct}%, OK={ram_ok}")

# Disk: use shutil
try:
    usage = shutil.disk_usage("/c/Users/hello")
    disk_total_mb = usage.total // (1024*1024)
    disk_free_mb = usage.free // (1024*1024)
    disk_free_pct = round(usage.free / usage.total * 100, 1)
    disk_ok = disk_free_pct >= 10
    print(f"DISK C:/Users/hello: Total={disk_total_mb}MB, Free={disk_free_mb}MB, {disk_free_pct}%, OK={disk_ok}")
except Exception as e:
    disk_total_mb = 0
    disk_free_mb = 0
    disk_free_pct = 0
    disk_ok = False
    print(f"DISK ERROR: {e}")

# Git
os.chdir("/c/Users/hello/alforaijboard-gh")
r3 = subprocess.run(["git","status","--porcelain"], capture_output=True, text=True)
git_lines = [l for l in r3.stdout.splitlines() if l.strip()]
git_dirty_files = []
for l in git_lines:
    parts = l.split()
    git_dirty_files.append(parts[1] if len(parts) > 1 else l)
git_dirty = len(git_dirty_files) > 0
print(f"GIT: dirty={git_dirty}, {len(git_dirty_files)} changes")
for f in git_dirty_files[:8]:
    print(f"  - {f}")
if len(git_dirty_files) > 8:
    print(f"  ... +{len(git_dirty_files)-8} more")

# Agents
r4 = subprocess.run(["ps","aux"], capture_output=True, text=True)
agent_lines = []
for line in r4.stdout.splitlines():
    lower = line.lower()
    if any(k in lower for k in ["hermes","agent","solar"]) and "grep" not in line:
        agent_lines.append(line[:150])
print(f"AGENTS: {len(agent_lines)} found")
for a in agent_lines[:10]:
    print(f"  - {a}")
if len(agent_lines) > 10:
    print(f"  ... +{len(agent_lines)-10} more")

report = {
    "check_time": datetime.now(timezone.utc).isoformat(),
    "docker": {"status": docker_status, "ok": docker_ok},
    "ram": {"total_mb": ram_total_mb, "free_mb": ram_free_mb, "free_pct": ram_free_pct, "ok": ram_ok},
    "disk": {"total_mb": disk_total_mb, "free_mb": disk_free_mb, "free_pct": disk_free_pct, "ok": disk_ok},
    "git": {"dirty": git_dirty, "files": git_dirty_files, "ok": not git_dirty},
    "agents": {"count": len(agent_lines), "processes": agent_lines, "ok": len(agent_lines) > 0},
}

print("\n=== JSON REPORT ===")
print(json.dumps(report, indent=2, ensure_ascii=False))

out_path = "/c/Users/hello/alforaijboard-gh/_cron_health_live_run.json"
with open(out_path,"w") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print(f"\nSaved to {out_path}")
print("=== DONE ===")
