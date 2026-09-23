import shutil, os
p = r"C:\Users\hello"
print(f"path: {p}")
print(f"exists: {os.path.exists(p)}")
print(f"isdir: {os.path.isdir(p)}")
d = shutil.disk_usage(p)
print(f"free={d.free/1024**3:.1f} total={d.total/1024**3:.1f} pct={(d.free/d.total)*100:.1f}")
