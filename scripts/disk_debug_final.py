import subprocess

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return r.stdout.strip(), r.stderr.strip(), r.returncode

print("=== 1. wmic disk ===")
out, err, rc = run('wmic logicaldisk where "DeviceID=\\"C:\\"" get Size,FreeSpace /value')
print(f"rc={rc}")
print(f"out: [{out}]")
print(f"err: [{err[:100] if err else 'none'}]")

print("\n=== 2. python3 shutil disk ===")
out2, err2, rc2 = run("python3 /c/Users/hello/alforaijboard-gh/scripts/shutil_test.py")
print(f"rc={rc2}")
print(f"out: [{out2}]")
print(f"err: [{err2[:100] if err2 else 'none'}]")
